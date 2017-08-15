from flask import Blueprint

from .views import IndexView
from apps.users.views import SessionsView


bp = Blueprint('general', __name__)

view_func = IndexView.as_view('index_view')
bp.add_url_rule('/', view_func=view_func)

view_func = SessionsView.as_view('sessions_view')
bp.add_url_rule('/sessions/', view_func=view_func)
