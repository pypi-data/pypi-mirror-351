from flask import Flask

def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object('config.Config')

    from .auth import auth_bp
    from .main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app
