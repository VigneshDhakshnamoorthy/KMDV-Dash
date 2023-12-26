from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    projects = db.Column(db.String(1024))  
    
    def __init__(self, username, password, projects=None):
        self.username = username
        self.password = password
        self.projects = ",".join(projects) if projects else None

    def get_projects_list(self):
        return self.projects.split(",") if self.projects else []