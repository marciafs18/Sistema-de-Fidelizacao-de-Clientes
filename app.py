from flask import Flask, render_template, redirect, url_for
from flask_login import current_user
from config import Config
from extensions import db, login_manager
from models import Usuario
from datetime import datetime, date


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Faça login para continuar.'

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    from auth.routes import auth_bp
    from crm.routes import crm_bp
    from financeiro.routes import fin_bp
    from fidelidade.routes import fid_bp
    from loja.routes import loja_bp
    from cliente_app.routes import cli_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(crm_bp, url_prefix='/crm')
    app.register_blueprint(fin_bp, url_prefix='/financeiro')
    app.register_blueprint(fid_bp, url_prefix='/fidelidade')
    app.register_blueprint(loja_bp, url_prefix='/loja')
    app.register_blueprint(cli_bp, url_prefix='/app')

    @app.route('/')
    def index():
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.perfil == 'CLI':
            return redirect(url_for('cli.painel'))
        return redirect(url_for('loja.painel'))

    @app.errorhandler(403)
    def erro_403(e):
        return render_template('errors/403.html'), 403

    @app.context_processor
    def inject_hoje():
        return {'hoje': date.today()}

    with app.app_context():
        db.create_all()
        _bootstrap_admin()

    return app


def _bootstrap_admin():
    """Cria o administrador inicial se não existir.
    Idempotente — executado a cada cold start no Vercel.
    No Vercel, o banco em /tmp começa vazio, então o admin é recriado."""
    if Usuario.query.filter_by(perfil='ADM').count() == 0:
        adm = Usuario(nome='Administrador', email='admin@admin.com',
                      perfil='ADM', primeiro_acesso=False)
        adm.set_senha('admin123')
        db.session.add(adm)
        db.session.commit()
        print('>>> Admin criado: admin@admin.com / admin123')


# Exposição no nível do módulo — o Vercel detecta esta variável
app = create_app()


if __name__ == '__main__':
    app.run(debug=True)
