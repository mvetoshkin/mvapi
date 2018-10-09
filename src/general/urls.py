from flask import Blueprint

from .views import HealthCheckView, IndexView


bp = Blueprint('general', __name__)

view_func = IndexView.as_view('index_view')
bp.add_url_rule('/', view_func=view_func)

view_func = HealthCheckView.as_view('health_check_view')
bp.add_url_rule('/health/', view_func=view_func)
