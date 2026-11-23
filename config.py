import os


def _is_vercel():
    return os.environ.get('VERCEL') == '1' or os.environ.get('VERCEL_ENV') is not None


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-mude-em-producao')

    # No Vercel: SQLite em /tmp (descartável). Local: arquivo relativo.
    if _is_vercel():
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/poc.db'
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///poc.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    QR_TOKEN_EXPIRATION = 300
    QR_SIGNING_KEY = os.environ.get('QR_SIGNING_KEY', 'qr-signing-key-dev')

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = _is_vercel()
    PERMANENT_SESSION_LIFETIME = 3600
