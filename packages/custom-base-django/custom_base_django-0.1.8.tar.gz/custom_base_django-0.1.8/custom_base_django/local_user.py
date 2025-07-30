import contextvars

_user_ctx_var = contextvars.ContextVar("user", default=None)

def set_current_user(user):
    _user_ctx_var.set(user)

def get_current_user():
    return _user_ctx_var.get()