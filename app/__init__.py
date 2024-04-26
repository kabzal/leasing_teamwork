from flask import Flask
from flask_login import LoginManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config
from .views import main_bl, auth_bl, admin_bl
from .models import User

engine = create_engine(Config.DB_URI)
Session = sessionmaker(bind=engine)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Для получения доступа к данной странице необходимо авторизоваться'
    login_manager.login_message_category = 'success'

    @app.before_request
    def create_db_session():
        if not hasattr(app, 'db_session'):
            app.db_session = Session()

    @app.teardown_request
    def remove_db_session(response):
        if hasattr(app, 'db_session'):
            app.db_session.close()
        return response

    @login_manager.user_loader
    def load_user(user_id):
        print("Loading user")
        return app.db_session.query(User).get(user_id)

    app.register_blueprint(main_bl)
    app.register_blueprint(auth_bl)
    app.register_blueprint(admin_bl)

    return app
