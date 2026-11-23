from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

# ---------- ENUM ----------
PERFIS = ('ADM', 'FUNC', 'CLI')

FORMAS_PARCELA = ['dinheiro', 'pix', 'cartao_credito', 'cartao_debito', 'boleto', 'crediario', 'transferencia']
FORMAS_RESGATE = ['dinheiro', 'pix', 'cartao_credito', 'cartao_debito', 'transferencia',
                  'desconto_em_compra', 'produto', 'credito_na_conta']

ROTULOS_FORMA = {
    'dinheiro': 'Dinheiro', 'pix': 'PIX', 'cartao_credito': 'Cartão de Crédito',
    'cartao_debito': 'Cartão de Débito', 'boleto': 'Boleto', 'crediario': 'Crediário',
    'transferencia': 'Transferência', 'desconto_em_compra': 'Desconto em Nova Compra',
    'produto': 'Produto (Brinde)', 'credito_na_conta': 'Crédito na Conta'
}

TIPOS_MOV_PONTOS = ('credito_pagamento', 'debito_resgate', 'estorno_resgate',
                    'concessao_administrativa', 'ajuste_administrativo',
                    'debito_venda')

# ---------- MODELOS ----------
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(10), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    primeiro_acesso = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    criado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)

    cliente = db.relationship('Cliente', backref='usuario', uselist=False, foreign_keys='Cliente.usuario_id')

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    @property
    def is_active(self):
        return self.ativo


class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(20))
    ativo = db.Column(db.Boolean, default=True)
    # Vínculo obrigatório 1:1 com usuário CLI
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    vendas = db.relationship('Venda', backref='cliente', lazy=True)
    mov_pontos = db.relationship('MovimentacaoPontos', backref='cliente', lazy=True)
    resgates = db.relationship('Resgate', backref='cliente', lazy=True)

    @property
    def saldo_pontos(self):
        total = 0
        for m in self.mov_pontos:
            if m.tipo in ('credito_pagamento', 'estorno_resgate',
                        'concessao_administrativa'):
                total += m.pontos
            elif m.tipo in ('debito_resgate', 'ajuste_administrativo', 'debito_venda'):
                total -= m.pontos
        return total


class Venda(db.Model):
    __tablename__ = 'vendas'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    valor_total = db.Column(db.Float, nullable=False)
    num_parcelas = db.Column(db.Integer, nullable=False)
    data_venda = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    originada_por_qr = db.Column(db.Boolean, default=False)

    parcelas = db.relationship('Parcela', backref='venda', lazy=True, cascade='all, delete-orphan')


class Parcela(db.Model):
    __tablename__ = 'parcelas'
    id = db.Column(db.Integer, primary_key=True)
    venda_id = db.Column(db.Integer, db.ForeignKey('vendas.id'), nullable=False)
    numero = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    vencimento = db.Column(db.Date, nullable=False)
    forma_prevista = db.Column(db.String(30), nullable=True)
    forma_realizada = db.Column(db.String(30), nullable=True)
    pago = db.Column(db.Boolean, default=False)
    data_pagamento = db.Column(db.DateTime, nullable=True)
    usuario_baixa_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)


class Resgate(db.Model):
    __tablename__ = 'resgates'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    pontos = db.Column(db.Integer, nullable=False)
    valor_equivalente = db.Column(db.Float, default=0.0)
    forma_pagamento = db.Column(db.String(30), nullable=False)
    observacao = db.Column(db.String(255))
    status = db.Column(db.String(20), default='ativo')  # ativo / cancelado
    data = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_operador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))


class MovimentacaoPontos(db.Model):
    __tablename__ = 'movimentacoes_pontos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    venda_id = db.Column(db.Integer, db.ForeignKey('vendas.id'), nullable=True)
    tipo = db.Column(db.String(30), nullable=False)
    pontos = db.Column(db.Integer, nullable=False)
    descricao = db.Column(db.String(255))
    observacao = db.Column(db.String(255))
    resgate_id = db.Column(db.Integer, db.ForeignKey('resgates.id'), nullable=True)
    parcela_id = db.Column(db.Integer, db.ForeignKey('parcelas.id'), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    data = db.Column(db.DateTime, default=datetime.utcnow)


class LogAuditoria(db.Model):
    __tablename__ = 'log_auditoria'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    acao = db.Column(db.String(80), nullable=False)
    entidade = db.Column(db.String(40))
    entidade_id = db.Column(db.Integer)
    detalhe = db.Column(db.String(255))
    data = db.Column(db.DateTime, default=datetime.utcnow)
