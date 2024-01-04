from datetime import datetime as dat
from flask import Blueprint, render_template, request, session
from flask_login import current_user, login_required
from routes.enumLinks import FileAssociate

from utils.dataUtil import getSheetNames, load_tables, weekDays
from asyncio import to_thread

WSRPage = Blueprint("WSRPage", __name__, template_folder="templates")


@WSRPage.route("/<template>", methods=["GET", "POST"])
@login_required
async def pages(template):
    if current_user.is_authenticated:
        project_list = current_user.get_projects_list()
        if template in project_list:
            if template != "favicon.ico":
                if not template in FileAssociate.keys():
                    return render_template("accounts/404.html")

            options_week = (
                await to_thread(getSheetNames, FileAssociate.get_value(template))
                if template != "favicon.ico"
                else await to_thread(getSheetNames, FileAssociate.ONETRACKER.value)
            )
            options_week = await options_week
            if request.method == "POST":
                selected_option = request.form.get("selected_option")
                session["selected_option"] = selected_option
            elif request.method == "GET":
                selected_option = options_week[0]
                session["selected_option"] = options_week[0]

            tables_fromsheet = (
                await to_thread(
                    load_tables, FileAssociate.get_value(template), selected_option
                )
                if template != "favicon.ico"
                else await to_thread(
                    load_tables, FileAssociate.ONETRACKER.value, selected_option
                )
            )
            tables_fromsheet = await tables_fromsheet
            return render_template(
                "pages/pages.html",
                dropdown_week=options_week,
                pageName=template,
                selected_dropdown=selected_option,
                weekdays=weekDays(selected_option),
                utilization_task_wise=tables_fromsheet[0].to_html(
                    classes="table caption-top table-bordered table-hover", index=False
                ),
                utilization_resource_wise=tables_fromsheet[1].to_html(
                    classes="table caption-top table-bordered table-hover", index=False
                ),
                task_last_week=tables_fromsheet[2].to_html(
                    classes="table caption-top table-bordered table-hover", index=False
                ),
                task_current_week=tables_fromsheet[3].to_html(
                    classes="table caption-top table-bordered table-hover", index=False
                ),
                defect=tables_fromsheet[4].to_html(
                    classes="table caption-top table-bordered table-hover", index=False
                ),
                summary=tables_fromsheet[5].to_html(
                    classes="table caption-top table-bordered table-hover", index=False
                ),
                weekDatasummary=tables_fromsheet[6].to_html(
                    classes="table caption-top table-bordered table-hover", index=False
                ),
                monthDatasummary=tables_fromsheet[7].to_html(
                    classes="table caption-top table-bordered table-hover", index=False
                ),
            )
        else:
            return render_template("accounts/wsrAuth.html")
