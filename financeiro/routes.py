from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import (Venda, Parcela, Cliente, MovimentacaoPontos, LogAuditoria,
                    FORMAS_PARCELA, ROTULOS_FORMA)
from decorators import loja_required
from datetime import datetime, timedelta
from sqlalchemy import or_

fin_bp = Blueprint('financeiro', __name__)

# ---------- LISTAGEM DE PARCELAS (Fase D — pós-venda) ----------
@fin_bp.route('/parcelas')
@login_required
@loja_required
def parcelas():
    status = request.args.get('status', '')
    venc_de = request.args.get('venc_de', '')
    venc_ate = request.args.get('venc_ate', '')
    forma = request.args.get('forma', '')
    cliente_q = request.args.get('cliente_q', '').strip()

    query = Parcela.query.join(Venda).join(Cliente)
    if status == 'paga':
        query = query.filter(Parcela.pago == True)
    elif status == 'aberta':
        query = query.filter(Parcela.pago == False,
                             Parcela.vencimento >= datetime.now().date())
    elif status == 'atrasada':
        query = query.filter(Parcela.pago == False,
                             Parcela.vencimento < datetime.now().date())
    if venc_de:
        query = query.filter(Parcela.vencimento >= datetime.strptime(venc_de, '%Y-%m-%d').date())
    if venc_ate:
        query = query.filter(Parcela.vencimento <= datetime.strptime(venc_ate, '%Y-%m-%d').date())
    if forma:
        query = query.filter(Parcela.forma_realizada == forma)
    if cliente_q:
        query = query.filter(Cliente.nome.ilike(f'%{cliente_q}%'))

    lista = query.order_by(Parcela.vencimento).all()
    return render_template('financeiro/parcelas.html', parcelas=lista,
                           formas=FORMAS_PARCELA, rotulos=ROTULOS_FORMA,
                           filtros={'status': status, 'venc_de': venc_de,
                                    'venc_ate': venc_ate, 'forma': forma,
                                    'cliente_q': cliente_q})


# ---------- NOVA VENDA (Fases B, C, D) ----------
@fin_bp.route('/vendas/nova', methods=['GET', 'POST'])
@login_required
@loja_required
def nova_venda():
    clientes = Cliente.query.filter_by(ativo=True).order_by(Cliente.nome).all()

    cliente_pre_id = request.args.get('cliente_id', type=int)
    if not cliente_pre_id and request.method == 'POST':
        cliente_pre_id = request.form.get('cliente_id', type=int)
    cliente_pre = Cliente.query.get(cliente_pre_id) if cliente_pre_id else None
    originada_qr = request.args.get('originada_qr') == '1' or request.form.get('originada_qr') == '1'

    if request.method == 'POST':
        try:
            cliente_id = int(request.form['cliente_id'])
            valor_total = float(request.form['valor_total'])
            num_parcelas = int(request.form['num_parcelas'])
            primeiro_venc = datetime.strptime(request.form['primeiro_vencimento'], '%Y-%m-%d').date()
        except (KeyError, ValueError):
            flash('Dados inválidos. Verifique os campos.')
            return _render_form(clientes, cliente_pre, originada_qr)

        forma_prevista = request.form.get('forma_prevista') or None

        if valor_total <= 0:
            flash('Valor total deve ser maior que zero.')
            return _render_form(clientes, cliente_pre, originada_qr)
        if num_parcelas < 1:
            flash('Número de parcelas deve ser pelo menos 1.')
            return _render_form(clientes, cliente_pre, originada_qr)

        cliente = Cliente.query.get(cliente_id)
        if not cliente or not cliente.ativo:
            flash('Cliente inexistente ou inativo.')
            return _render_form(clientes, cliente_pre, originada_qr)

        if forma_prevista and forma_prevista not in FORMAS_PARCELA:
            flash('Forma prevista inválida para parcela.')
            return _render_form(clientes, cliente_pre, originada_qr)

        # ----- REGRA NOVA: saldo >= valor total -----
        pontos_exigidos = int(round(valor_total))
        saldo = cliente.saldo_pontos
        if saldo < pontos_exigidos:
            faltam = pontos_exigidos - saldo
            db.session.add(LogAuditoria(
                usuario_id=current_user.id, acao='venda_bloqueada_saldo',
                entidade='Cliente', entidade_id=cliente.id,
                detalhe=f'saldo={saldo} exigido={pontos_exigidos} faltam={faltam} qr={originada_qr}'))
            db.session.commit()
            flash(f'Saldo insuficiente. Cliente tem {saldo} pts, '
                  f'a venda exige {pontos_exigidos} pts. Faltam {faltam} pts. '
                  f'Esta regra não admite exceção.')
            return _render_form(clientes, cliente_pre, originada_qr)

        # ----- Criação transacional: venda + parcelas + débito de pontos -----
        try:
            v = Venda(cliente_id=cliente.id, valor_total=valor_total,
                      num_parcelas=num_parcelas, usuario_id=current_user.id,
                      originada_por_qr=originada_qr)
            db.session.add(v)
            db.session.flush()

            valor_p = round(valor_total / num_parcelas, 2)
            for i in range(num_parcelas):
                db.session.add(Parcela(
                    venda_id=v.id, numero=i+1, valor=valor_p,
                    vencimento=primeiro_venc + timedelta(days=30*i),
                    forma_prevista=forma_prevista))

            # Débito dos pontos na criação da venda
            db.session.add(MovimentacaoPontos(
                cliente_id=cliente.id, tipo='debito_venda',
                pontos=pontos_exigidos,
                descricao=f'Entrada da venda #{v.id}',
                venda_id=v.id, usuario_id=current_user.id))

            db.session.add(LogAuditoria(
                usuario_id=current_user.id, acao='criar_venda',
                entidade='Venda', entidade_id=v.id,
                detalhe=f'cliente={cliente.id} valor={valor_total} '
                        f'parcelas={num_parcelas} debito_pts={pontos_exigidos} qr={originada_qr}'))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar venda: {e}')
            return _render_form(clientes, cliente_pre, originada_qr)

        flash(f'Venda #{v.id} criada para {cliente.nome} — {num_parcelas}x de '
              f'R$ {valor_p:.2f}. {pontos_exigidos} pontos debitados como entrada.')
        return redirect(url_for('financeiro.parcelas'))

    return _render_form(clientes, cliente_pre, originada_qr)


def _render_form(clientes, cliente_pre, originada_qr):
    return render_template('financeiro/nova_venda.html',
                           clientes=clientes, cliente_pre=cliente_pre,
                           formas=FORMAS_PARCELA, rotulos=ROTULOS_FORMA,
                           originada_qr=originada_qr)


# ---------- BAIXA DE PARCELA (Fase C — forma obrigatória) ----------
@fin_bp.route('/parcelas/<int:pid>/pagar', methods=['POST'])
@login_required
@loja_required
def pagar_parcela(pid):
    p = Parcela.query.get_or_404(pid)
    if p.pago:
        flash('Parcela já paga.')
        return redirect(url_for('financeiro.parcelas'))
    forma = request.form.get('forma_realizada')
    if forma not in FORMAS_PARCELA:
        flash('Forma de pagamento obrigatória e válida.')
        return redirect(url_for('financeiro.parcelas'))

    p.pago = True
    p.data_pagamento = datetime.utcnow()
    p.forma_realizada = forma
    p.usuario_baixa_id = current_user.id

    pontos = int(p.valor)
    if pontos > 0:
        db.session.add(MovimentacaoPontos(
            cliente_id=p.venda.cliente_id, tipo='credito_pagamento',
            pontos=pontos,
            descricao=f'Pagamento parcela {p.numero}/{p.venda.num_parcelas}',
            parcela_id=p.id, usuario_id=current_user.id))
    db.session.add(LogAuditoria(usuario_id=current_user.id, acao='baixar_parcela',
                                entidade='Parcela', entidade_id=p.id,
                                detalhe=f'forma={forma}'))
    db.session.commit()
    flash(f'Parcela paga com {ROTULOS_FORMA[forma]}. {pontos} pontos creditados.')
    return redirect(url_for('financeiro.parcelas'))
