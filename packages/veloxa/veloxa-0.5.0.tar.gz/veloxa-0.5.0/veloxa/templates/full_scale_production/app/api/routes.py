from flask import render_template
from . import api_bp

@api_bp.route('/api')
def main_index():
    return "API"
