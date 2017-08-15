from flask import Blueprint

from .views import UsersView


bp = Blueprint('users', __name__, url_prefix='/users')

view_func = UsersView.as_view('users_view')
bp.add_url_rule('/', view_func=view_func)
bp.add_url_rule('/<int:user_id>/', view_func=view_func)
