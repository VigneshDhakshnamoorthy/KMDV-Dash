import asyncio
from typing import Coroutine

from pandas.core.frame import DataFrame
from flask import Blueprint, render_template
from flask_login import current_user, login_required
from routes.enumLinks import getUserName

from utils.dataUtil import load_data


InformationPage = Blueprint("InformationPage", __name__, template_folder="templates")


@InformationPage.route("/Automation", methods=["GET", "POST"])
@login_required
async def Automation() -> str:
    tables_fromsheet:Coroutine[DataFrame] = await asyncio.to_thread(
        load_data, "dataSources/monthData/dashSummary.xlsx", "Metrics", 0, 11
    )
    tables_fromsheet: DataFrame = await tables_fromsheet
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
async def Technology() -> str:
    tech1:Coroutine[DataFrame] = await asyncio.to_thread(
        load_data, "dataSources/monthData/dashSummary.xlsx", "Technology", 0, 9
    )
    tech2:Coroutine[DataFrame] = await asyncio.to_thread(
        load_data, "dataSources/monthData/dashSummary.xlsx", "Technology", 10, 17
    )
    tech1:DataFrame = await tech1
    tech2:DataFrame = await tech2
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
async def Applications() -> str:
    tables_fromsheet:Coroutine[DataFrame] = await asyncio.to_thread(
        load_data, "dataSources/monthData/dashSummary.xlsx", "Metrics", 0, 11
    )
    tables_fromsheet: DataFrame = await tables_fromsheet
    return render_template(
        "pages/qaApplications.html",
        userName=getUserName(current_user),
        selected_project = "QA APPLICATIONS",
        tables_fromsheet=tables_fromsheet.to_html(
            classes="table caption-top table-bordered table-hover", index=False
        ),
    )
