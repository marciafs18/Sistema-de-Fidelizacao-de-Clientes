from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app
from extensions import db
from models import Cliente, Parcela, LogAuditoria, Venda
from decorators import loja_required
from datetime import datetime

loja_bp = Blueprint('loja', __name__)

def _serializer():
    return URLSafeTimedSerializer(current_app.config['QR_SIGNING_KEY'])

def gerar_token_qr(cliente):
    return _serializer().dumps({'cliente_id': cliente.id})

def validar_token_qr(token):
    try:
        data = _serializer().loads(token,
                                   max_age=current_app.config['QR_TOKEN_EXPIRATION'])
        return Cliente.query.get(data.get('cliente_id'))
    except SignatureExpired:
        return 'expired'
    except BadSignature:
        return None


@loja_bp.route('/painel')
@login_required
@loja_required
def painel():
    hoje = datetime.now().date()
    kpis = {
        'vendas_hoje': Venda.query.filter(db.func.date(Venda.data_venda) == hoje).count(),
        'parcelas_hoje': Parcela.query.filter(Parcela.pago == False,
                                              Parcela.vencimento == hoje).count(),
        'parcelas_atrasadas': Parcela.query.filter(Parcela.pago == False,
                                                   Parcela.vencimento < hoje).count(),
    }
    return render_template('loja/painel.html', kpis=kpis)


@loja_bp.route('/ler-qrcode')
@login_required
@loja_required
def ler_qrcode():
    return render_template('loja/leitor_qr.html')


@loja_bp.route('/api/qrcode/validar', methods=['POST'])
@login_required
@loja_required
def api_validar_qr():
    data = request.get_json(silent=True) or {}
    token = data.get('token', '').strip()
    if not token:
        return jsonify({'ok': False, 'erro': 'Token ausente'}), 400
    resultado = validar_token_qr(token)
    if resultado == 'expired':
        db.session.add(LogAuditoria(usuario_id=None, acao='qr_expirado'))
        db.session.commit()
        return jsonify({'ok': False, 'erro': 'QR expirado. Peça ao cliente renovar.'}), 400
    if not resultado:
        db.session.add(LogAuditoria(usuario_id=None, acao='qr_invalido'))
        db.session.commit()
        return jsonify({'ok': False, 'erro': 'QR inválido'}), 400
    cliente = resultado
    db.session.add(LogAuditoria(usuario_id=None, acao='qr_lido',
                                entidade='Cliente', entidade_id=cliente.id))
    db.session.commit()
    return jsonify({
        'ok': True,
        'cliente': {'id': cliente.id, 'nome': cliente.nome,
                    'pontos': cliente.saldo_pontos}
    })

@loja_bp.route('/relatorios/vendas-bloqueadas')
@login_required
@loja_required
def relatorio_vendas_bloqueadas():
    logs = LogAuditoria.query.filter_by(acao='venda_bloqueada_saldo')\
        .order_by(LogAuditoria.data.desc()).all()
    total = len(logs)
    return render_template('loja/relatorio_bloqueios.html', logs=logs, total=total)
