from functools import wraps
from flask import abort
from flask_login import current_user

def perfil_required(*perfis):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.perfil not in perfis:
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator

def adm_required(f):
    return perfil_required('ADM')(f)

def loja_required(f):
    return perfil_required('ADM', 'FUNC')(f)

def cli_required(f):
    return perfil_required('CLI')(f)
