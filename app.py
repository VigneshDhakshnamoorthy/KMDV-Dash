import asyncio
from flask import Flask, render_template
from flask_login import (
    LoginManager,
    current_user,
    login_required,
)


from database.database import init_db
from database.models import User
from routes.authenticationRoutes import AuthenticationPage
from routes.dashRoutes import DashboardPage
from routes.enumLinks import FileAssociate
from routes.wsrRoutes import WSRPage


app = Flask(__name__)
app.register_blueprint(AuthenticationPage)
app.register_blueprint(DashboardPage, url_prefix="/home")
app.register_blueprint(WSRPage, url_prefix="/wsr")
init_db(app)


login_manager = LoginManager(app)
login_manager.login_view = "AuthenticationPage.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.errorhandler(404)
def not_found(e):
    return render_template("accounts/404.html")

@app.route("/home", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
@login_required
async def index():
    if current_user.is_authenticated:
        project_list = sorted(await asyncio.to_thread(current_user.get_projects_list))
        filtered_projects = [project for project in project_list if FileAssociate.get_value(project) is not None]
        return render_template("pages/index.html", userName=current_user.username, projects=project_list, filtered_project=filtered_projects)


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=6963, threaded=True)
