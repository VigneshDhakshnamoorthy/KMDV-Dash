import asyncio
from flask import Blueprint, render_template
from flask_login import login_required

from utils.dataUtil import load_data


InformationPage = Blueprint("InformationPage", __name__, template_folder="templates")


@InformationPage.route("/Project", methods=["GET", "POST"])
@login_required
async def Project():
    tables_fromsheet = await asyncio.to_thread(
        load_data, "dataSources/monthData/dashSummary.xlsx", "Metrics", 0, 11
    )
    tables_fromsheet = await tables_fromsheet
    return render_template(
        "tables/projectInformation.html",
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
        tech1=tech1.to_html(
            classes="table caption-top table-bordered table-hover table-striped table_header", index=False
        ),       
        tech2=tech2.to_html(
            classes="table caption-top table-bordered table-hover table-striped table_header", index=False
        ),
    )
