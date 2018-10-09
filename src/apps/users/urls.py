from flask import Blueprint

from general.urls import bp as general_bp
from .views import UsersView, SessionsView

bp = Blueprint('users', __name__, url_prefix='/users')

view_func = UsersView.as_view('users_view')
bp.add_url_rule('/', view_func=view_func)
bp.add_url_rule('/<uritemplate(user_id, uuid):user_id>/', view_func=view_func)


# General bluepring urls

view_func = SessionsView.as_view('sessions_view')
general_bp.add_url_rule('/sessions/', view_func=view_func)
