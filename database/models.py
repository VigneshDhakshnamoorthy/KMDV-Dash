from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    projects = db.Column(db.String(1024), nullable=False)
    user_type = db.Column(db.String(10), nullable=False)

    def __init__(self, email, password, projects=None, user_type='normal'):
        self.email = email
        self.password = password
        self.projects = ",".join(projects) if projects else None
        self.user_type = user_type

    def get_projects_list(self):
        return self.projects.split(",") if self.projects else []