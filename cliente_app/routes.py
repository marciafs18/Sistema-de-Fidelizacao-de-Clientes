from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Parcela, MovimentacaoPontos, ROTULOS_FORMA, TIPOS_MOV_PONTOS
from decorators import cli_required
from loja.routes import gerar_token_qr

cli_bp = Blueprint('cli', __name__)

@cli_bp.route('/painel')
@login_required
@cli_required
def painel():
    cliente = current_user.cliente
    if not cliente:
        flash('Usuário sem cliente vinculado.')
        return redirect(url_for('auth.logout'))

    parcelas = Parcela.query.join(cliente.vendas[0].__class__ if cliente.vendas else Parcela) \
        if False else Parcela.query.filter(
            Parcela.venda_id.in_([v.id for v in cliente.vendas]),
            Parcela.pago == False
        ).order_by(Parcela.vencimento).all()

    filtro_tipo = request.args.get('tipo_mov', '')
    movs_q = MovimentacaoPontos.query.filter_by(cliente_id=cliente.id)
    if filtro_tipo:
        movs_q = movs_q.filter_by(tipo=filtro_tipo)
    movs = movs_q.order_by(MovimentacaoPontos.data.desc()).all()

    return render_template('cliente_app/painel.html',
                           cliente=cliente, parcelas=parcelas,
                           movs=movs, rotulos=ROTULOS_FORMA,
                           tipos=TIPOS_MOV_PONTOS, filtro_tipo=filtro_tipo)


@cli_bp.route('/qrcode')
@login_required
@cli_required
def qrcode():
    cliente = current_user.cliente
    token = gerar_token_qr(cliente)
    return render_template('cliente_app/qrcode.html', cliente=cliente, token=token)
