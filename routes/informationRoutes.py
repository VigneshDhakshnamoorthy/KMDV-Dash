import asyncio
from flask import Blueprint, render_template
from flask_login import current_user, login_required
from routes.enumLinks import getUserName

from utils.dataUtil import load_data


InformationPage = Blueprint("InformationPage", __name__, template_folder="templates")


@InformationPage.route("/Automation", methods=["GET", "POST"])
@login_required
async def Automation():
    tables_fromsheet = await asyncio.to_thread(
        load_data, "dataSources/monthData/dashSummary.xlsx", "Metrics", 0, 11
    )
    tables_fromsheet = await tables_fromsheet
    return render_template(
        "tables/automationInformation.html",
        userName=getUserName(current_user),
        selected_project = "AUTOMATION METRICS",
        tables_fromsheet=tables_fromsheet.to_html(
            classes="table caption-top table-bordered table-hover", index=False
        ),
    )


@InformationPage.route("/Technology", methods=["GET", "POST"])
@login_required
async def Technology():
    tech1 = await asyncio.to_thread(
        load_data, "dataSources/monthData/dashSummary.xlsx", "Technology", 0, 9
    )
    tech2 = await asyncio.to_thread(
        load_data, "dataSources/monthData/dashSummary.xlsx", "Technology", 10, 17
    )
    tech1 = await tech1
    tech2 = await tech2
    return render_template(
        "tables/technologyInformation.html",
        userName=getUserName(current_user),
        selected_project = "TECHNOLOGY INFORMATION",
        tech1=tech1.to_html(
            classes="table caption-top table-bordered table-hover table-striped table_header",
            index=False,
        ),
        tech2=tech2.to_html(
            classes="table caption-top table-bordered table-hover table-striped table_header",
            index=False,
        ),
    )


@InformationPage.route("/Applications", methods=["GET", "POST"])
@login_required
async def Applications():
    tables_fromsheet = await asyncio.to_thread(
        load_data, "dataSources/monthData/dashSummary.xlsx", "Metrics", 0, 11
    )
    tables_fromsheet = await tables_fromsheet
    return render_template(
        "pages/qaApplications.html",
        userName=getUserName(current_user),
        selected_project = "QA APPLICATIONS",
        tables_fromsheet=tables_fromsheet.to_html(
            classes="table caption-top table-bordered table-hover", index=False
        ),
    )
