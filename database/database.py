import os
from .models import db

def init_db(app):
    database_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "db")
    os.makedirs(database_folder, exist_ok=True)
    database_file_path = os.path.join(database_folder, "user.db")
    app.config["SECRET_KEY"] = "ces_secret_key"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_file_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()