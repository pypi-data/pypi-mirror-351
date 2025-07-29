from . import auth_bp

@auth_bp.route('/auth')
def auth_home():
    return "Auth Blueprint"
