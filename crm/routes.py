from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Cliente, Usuario, MovimentacaoPontos, LogAuditoria
from decorators import loja_required, adm_required
from sqlalchemy import or_

crm_bp = Blueprint('crm', __name__)

@crm_bp.route('/clientes')
@login_required
@loja_required
def clientes():
    q = request.args.get('q', '').strip()
    status = request.args.get('status', '')
    pontos_min = request.args.get('pontos_min', type=int)
    pontos_max = request.args.get('pontos_max', type=int)

    query = Cliente.query
    if q:
        like = f'%{q}%'
        query = query.filter(or_(Cliente.nome.ilike(like),
                                 Cliente.email.ilike(like),
                                 Cliente.telefone.ilike(like)))
    if status == 'ativo':
        query = query.filter(Cliente.ativo == True)
    elif status == 'inativo':
        query = query.filter(Cliente.ativo == False)

    clientes = query.order_by(Cliente.nome).all()

    if pontos_min is not None:
        clientes = [c for c in clientes if c.saldo_pontos >= pontos_min]
    if pontos_max is not None:
        clientes = [c for c in clientes if c.saldo_pontos <= pontos_max]

    return render_template('crm/clientes.html', clientes=clientes,
                           filtros={'q': q, 'status': status,
                                    'pontos_min': pontos_min, 'pontos_max': pontos_max})


@crm_bp.route('/clientes/novo', methods=['GET', 'POST'])
@login_required
@adm_required
def novo_cliente():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form.get('telefone', '')
        senha_inicial = request.form['senha_inicial']
        pontos_iniciais = int(request.form.get('pontos_iniciais') or 0)

        if Usuario.query.filter_by(email=email).first():
            flash('E-mail já cadastrado como usuário.')
            return render_template('crm/cliente_form.html')

        try:
            # Transação: usuário CLI + cliente + movimentação inicial
            u = Usuario(nome=nome, email=email, perfil='CLI', primeiro_acesso=True,
                        criado_por_id=current_user.id)
            u.set_senha(senha_inicial)
            db.session.add(u)
            db.session.flush()

            c = Cliente(nome=nome, email=email, telefone=telefone, usuario_id=u.id)
            db.session.add(c)
            db.session.flush()

            if pontos_iniciais > 0:
                db.session.add(MovimentacaoPontos(
                    cliente_id=c.id, tipo='concessao_administrativa',
                    pontos=pontos_iniciais,
                    descricao='Concessão inicial no cadastro',
                    usuario_id=current_user.id))

            db.session.add(LogAuditoria(usuario_id=current_user.id, acao='criar_cliente',
                                        entidade='Cliente', entidade_id=c.id))
            db.session.commit()
            flash('Cliente e usuário criados com sucesso.')
            return redirect(url_for('crm.clientes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar: {e}')
            return render_template('crm/cliente_form.html')

    return render_template('crm/cliente_form.html')


@crm_bp.route('/clientes/<int:cid>/editar', methods=['GET', 'POST'])
@login_required
@adm_required
def editar_cliente(cid):
    c = Cliente.query.get_or_404(cid)
    if request.method == 'POST':
        c.nome = request.form['nome']
        c.telefone = request.form.get('telefone', '')
        db.session.commit()
        flash('Cliente atualizado.')
        return redirect(url_for('crm.clientes'))
    return render_template('crm/cliente_form.html', cliente=c)

@crm_bp.route('/clientes/<int:cid>')
@login_required
@loja_required
def ficha_cliente(cid):
    c = Cliente.query.get_or_404(cid)
    return render_template('crm/cliente_ficha.html', cliente=c)
