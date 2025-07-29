from . import api_bp

@api_bp.route('/v1')
def api_v1():
    return "API v1 endpoint"
