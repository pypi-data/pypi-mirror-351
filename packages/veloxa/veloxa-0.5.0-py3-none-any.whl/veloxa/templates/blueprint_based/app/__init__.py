from flask import Flask, render_template

def create_app():
    app = Flask(__name__)

    from .auth import auth_bp
    from .blog import blog_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(blog_bp, url_prefix='/blog')

    @app.route("/")
    def home():
        return render_template('index.html')

    return app
