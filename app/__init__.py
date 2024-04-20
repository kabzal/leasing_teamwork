from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from instance.config import Config
from .views import main

engine = create_engine(Config.DB_URI)
Session = sessionmaker(bind=engine)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.before_request
    def create_db_session():
        if not hasattr(app, 'db_session'):
            app.db_session = Session()

    @app.teardown_request
    def remove_db_session(response):
        if hasattr(app, 'db_session'):
            app.db_session.close()
        return response

    app.register_blueprint(main)


    return app
