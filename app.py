import asyncio
from flask import Flask, render_template
from flask_login import (
    LoginManager,
    current_user,
    login_required,
)


from database.database import init_db
from database.models import User, db
from routes.authenticationRoutes import AuthenticationPage
from routes.dashRoutes import DashboardPage, year_list
from routes.enumLinks import FileAssociate, getUserName
from routes.informationRoutes import InformationPage
from routes.wsrRoutes import WSRPage
from utils.dataUtil import load_data, load_tables


app = Flask(__name__)
app.register_blueprint(AuthenticationPage)
app.register_blueprint(DashboardPage, url_prefix="/home")
app.register_blueprint(WSRPage, url_prefix="/wsr")
app.register_blueprint(InformationPage, url_prefix="/Information")

init_db(app)


login_manager = LoginManager(app)
login_manager.login_view = "AuthenticationPage.login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.errorhandler(404)
def not_found(e):
    return render_template("accounts/404.html")


@app.route("/home", methods=["GET"])
@app.route("/", methods=["GET"])
@login_required
async def index():
    if current_user.is_authenticated:
        tables_fromsheet = await asyncio.to_thread(
            load_data, "dataSources/monthData/dashSummary.xlsx", "Status",0,2
        )
        tables_fromsheet = await tables_fromsheet
        project_list = sorted(await asyncio.to_thread(current_user.get_projects_list))
        filtered_projects = [
            project
            for project in project_list
            if FileAssociate.get_value(project) is not None
        ]
        return render_template(
            "pages/index.html",
            userName=getUserName(current_user),
            projects=project_list,
            filtered_project=filtered_projects,
            year_list=year_list,
            project_table = tables_fromsheet.to_html(
                    classes="table caption-top table-bordered table-hover", index=False
                ),
            project_table_html = tables_fromsheet
        )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=6963, threaded=True)


# if __name__ == "__main__":
#     from waitress import serve
#     app.debug = True
#     serve(app, host="0.0.0.0", port=6963, threads=4)
