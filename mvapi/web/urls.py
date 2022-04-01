from flask import Blueprint

from mvapi.web.views.api import APIView

api_bp = Blueprint('api', __name__, url_prefix='/api')
view_func = APIView.as_view('api_view')

api_bp.add_url_rule(
    '',
    view_func=view_func
)

api_bp.add_url_rule(
    '<string:resource_type>',
    view_func=view_func
)

api_bp.add_url_rule(
    '<string:resource_type>/<string:resource_id>',
    view_func=view_func
)

api_bp.add_url_rule(
    '<string:resource_type>/<string:resource_id>/relationships/'
    '<string:relationship_type>',
    view_func=view_func
)

api_bp.add_url_rule(
    '<string:resource_type>/<string:resource_id>/'
    '<string:related_relationship_type>',
    view_func=view_func
)
