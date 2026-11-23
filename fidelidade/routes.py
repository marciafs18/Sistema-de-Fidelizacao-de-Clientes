from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import (Cliente, Resgate, MovimentacaoPontos, LogAuditoria,
                    FORMAS_RESGATE, ROTULOS_FORMA)
from decorators import loja_required, adm_required

fid_bp = Blueprint('fidelidade', __name__)

@fid_bp.route('/clientes/<int:cid>/resgates/novo', methods=['GET', 'POST'])
@login_required
@loja_required
def novo_resgate(cid):
    c = Cliente.query.get_or_404(cid)
    if request.method == 'POST':
        pontos = int(request.form['pontos'])
        forma = request.form['forma_pagamento']
        valor_eq = float(request.form.get('valor_equivalente') or 0)
        obs = request.form.get('observacao', '')

        if forma not in FORMAS_RESGATE:
            flash('Forma de pagamento inválida para resgate.')
            return render_template('fidelidade/resgate.html', cliente=c,
                                   formas=FORMAS_RESGATE, rotulos=ROTULOS_FORMA)
        if pontos <= 0 or pontos > c.saldo_pontos:
            flash('Pontos inválidos ou insuficientes.')
            return render_template('fidelidade/resgate.html', cliente=c,
                                   formas=FORMAS_RESGATE, rotulos=ROTULOS_FORMA)
        if forma == 'produto' and not obs:
            flash('Descreva o produto entregue na observação.')
            return render_template('fidelidade/resgate.html', cliente=c,
                                   formas=FORMAS_RESGATE, rotulos=ROTULOS_FORMA)

        r = Resgate(cliente_id=c.id, pontos=pontos, valor_equivalente=valor_eq,
                    forma_pagamento=forma, observacao=obs, usuario_operador_id=current_user.id)
        db.session.add(r)
        db.session.flush()
        db.session.add(MovimentacaoPontos(
            cliente_id=c.id, tipo='debito_resgate', pontos=pontos,
            descricao=f'Resgate #{r.id} via {ROTULOS_FORMA[forma]}',
            resgate_id=r.id, usuario_id=current_user.id, observacao=obs))
        db.session.add(LogAuditoria(usuario_id=current_user.id, acao='criar_resgate',
                                    entidade='Resgate', entidade_id=r.id))
        db.session.commit()
        flash(f'Resgate #{r.id} registrado com {ROTULOS_FORMA[forma]}.')
        return redirect(url_for('crm.clientes'))
    return render_template('fidelidade/resgate.html', cliente=c,
                           formas=FORMAS_RESGATE, rotulos=ROTULOS_FORMA)


@fid_bp.route('/resgates/<int:rid>/cancelar', methods=['POST'])
@login_required
@adm_required
def cancelar_resgate(rid):
    r = Resgate.query.get_or_404(rid)
    if r.status != 'ativo':
        flash('Resgate já cancelado.')
        return redirect(url_for('crm.clientes'))
    r.status = 'cancelado'
    db.session.add(MovimentacaoPontos(
        cliente_id=r.cliente_id, tipo='estorno_resgate', pontos=r.pontos,
        descricao=f'Estorno do resgate #{r.id}', resgate_id=r.id,
        usuario_id=current_user.id))
    db.session.add(LogAuditoria(usuario_id=current_user.id, acao='cancelar_resgate',
                                entidade='Resgate', entidade_id=r.id))
    db.session.commit()
    flash('Resgate cancelado e pontos estornados.')
    return redirect(url_for('crm.clientes'))


@fid_bp.route('/clientes/<int:cid>/ajustar-pontos', methods=['GET', 'POST'])
@login_required
@adm_required
def ajustar_pontos(cid):
    c = Cliente.query.get_or_404(cid)
    if request.method == 'POST':
        delta = int(request.form['delta'])
        obs = request.form['observacao'].strip()
        if delta == 0:
            flash('Informe um valor diferente de zero.')
            return render_template('fidelidade/ajuste_pontos.html', cliente=c)
        if not obs:
            flash('Observação obrigatória.')
            return render_template('fidelidade/ajuste_pontos.html', cliente=c)
        if c.saldo_pontos + delta < 0:
            flash('Ajuste deixaria saldo negativo.')
            return render_template('fidelidade/ajuste_pontos.html', cliente=c)

        tipo = 'concessao_administrativa' if delta > 0 else 'ajuste_administrativo'
        db.session.add(MovimentacaoPontos(
            cliente_id=c.id, tipo=tipo, pontos=abs(delta),
            descricao=f'Ajuste administrativo ({delta:+d})',
            observacao=obs, usuario_id=current_user.id))
        db.session.add(LogAuditoria(usuario_id=current_user.id, acao='ajustar_pontos',
                                    entidade='Cliente', entidade_id=c.id,
                                    detalhe=f'delta={delta}'))
        db.session.commit()
        flash(f'Ajuste de {delta:+d} aplicado.')
        return redirect(url_for('crm.clientes'))
    return render_template('fidelidade/ajuste_pontos.html', cliente=c)

@fid_bp.route('/relatorios/pontos-por-origem')
@login_required
@loja_required
def relatorio_pontos_por_origem():
    from models import TIPOS_MOV_PONTOS
    agregado = {}
    for tipo in TIPOS_MOV_PONTOS:
        total = db.session.query(db.func.sum(MovimentacaoPontos.pontos))\
            .filter(MovimentacaoPontos.tipo == tipo).scalar() or 0
        agregado[tipo] = total
    return render_template('fidelidade/relatorio_pontos.html', agregado=agregado)
