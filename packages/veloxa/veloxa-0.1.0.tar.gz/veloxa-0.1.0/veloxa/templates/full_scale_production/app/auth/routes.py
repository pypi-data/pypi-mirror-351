from flask import render_template
from . import auth_bp

@auth_bp.route('/auth')
def main_index():
    return "Auth here"
