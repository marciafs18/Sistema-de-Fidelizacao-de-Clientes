from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import Usuario, LogAuditoria
from decorators import adm_required
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        u = Usuario.query.filter_by(email=email, ativo=True).first()
        if not u or not u.check_senha(senha):
            flash('Credenciais inválidas.')
            return render_template('auth/login.html')
        login_user(u)
        db.session.add(LogAuditoria(usuario_id=u.id, acao='login'))
        db.session.commit()
        if u.primeiro_acesso:
            flash('Troque sua senha no primeiro acesso.')
            return redirect(url_for('auth.trocar_senha'))
        if u.perfil == 'CLI':
            return redirect(url_for('cli.painel'))
        return redirect(url_for('loja.painel'))
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    db.session.add(LogAuditoria(usuario_id=current_user.id, acao='logout'))
    db.session.commit()
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/trocar-senha', methods=['GET', 'POST'])
@login_required
def trocar_senha():
    if request.method == 'POST':
        nova = request.form['nova_senha']
        if len(nova) < 6:
            flash('Senha mínima: 6 caracteres.')
            return render_template('auth/trocar_senha.html')
        current_user.set_senha(nova)
        current_user.primeiro_acesso = False
        db.session.commit()
        flash('Senha alterada.')
        return redirect(url_for('index'))
    return render_template('auth/trocar_senha.html')

# ---------- Gestão de usuários (ADM) ----------
@auth_bp.route('/usuarios')
@login_required
@adm_required
def usuarios():
    lista = Usuario.query.filter(Usuario.perfil.in_(['ADM', 'FUNC'])).all()
    return render_template('auth/usuarios.html', usuarios=lista)

@auth_bp.route('/usuarios/novo', methods=['GET', 'POST'])
@login_required
@adm_required
def novo_usuario():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        perfil = request.form['perfil']
        senha = request.form['senha']
        if perfil not in ('ADM', 'FUNC'):
            flash('Perfil inválido.')
            return render_template('auth/usuario_form.html')
        if Usuario.query.filter_by(email=email).first():
            flash('E-mail já cadastrado.')
            return render_template('auth/usuario_form.html')
        u = Usuario(nome=nome, email=email, perfil=perfil, primeiro_acesso=True,
                    criado_por_id=current_user.id)
        u.set_senha(senha)
        db.session.add(u)
        db.session.commit()
        db.session.add(LogAuditoria(usuario_id=current_user.id, acao='criar_usuario',
                                    entidade='Usuario', entidade_id=u.id))
        db.session.commit()
        flash('Usuário criado.')
        return redirect(url_for('auth.usuarios'))
    return render_template('auth/usuario_form.html')
