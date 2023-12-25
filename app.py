from datetime import datetime as dat
import os
from sqlite3 import IntegrityError
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)

import pandas as pd
from database.database import init_db
from database.forms import LoginForm, SignupForm
from database.models import User, db
from utils.zynaCharts import (
    BarChart,
    ColumnChart,
    LineChart,
    MultiColumnChart,
    MultiLineChart,
    SplineChart,
)

from utils.dataUtil import (
    filterDataSummary,
    getChartData,
    getRowResource,
    getSheetNames,
    load_data,
    load_tables,
    sum_columns_cost,
    sum_columns_resource,
    weekDays,
)


app = Flask(__name__)


login_manager = LoginManager(app)
login_manager.login_view = "login"

init_db(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# fileAssociate = {
#     "Form PF": "dataSources/WSR/FormPF.xlsx",
#     "OCP Tech": "dataSources/WSR/OneTracker.xlsx",
#     "Onetracker": "dataSources/WSR/OneTracker.xlsx",
#     "SICAV": "dataSources/WSR/OneTracker.xlsx",
#     "Treena": "dataSources/WSR/FormPF.xlsx",
#     "Beeqom": "dataSources/WSR/Beqom.xlsx",
#     "Corporate Actions": "dataSources/WSR/Corporate Action.xlsx",
#     "HRIS": "dataSources/WSR/HRIS.xlsx",
#     "ICS": "dataSources/WSR/ICS.xlsx",
#     "vEMS": "dataSources/WSR/vEMS.xlsx",
#     "Workday": "dataSources/WSR/workday.xlsx",
#     "FX Central": "dataSources/WSR/OneTracker.xlsx",
#     "Mercatus": "dataSources/WSR/OneTracker.xlsx",
#     "QA Smoke Test": "dataSources/WSR/OneTracker.xlsx",
# }

fileAssociate = {
    "Form PF": "dataSources/WSR/OneTracker.xlsx",
    "OCP Tech": "dataSources/WSR/OneTracker.xlsx",
    "Onetracker": "dataSources/WSR/OneTracker.xlsx",
    "SICAV": "dataSources/WSR/OneTracker.xlsx",
    "Treena": "dataSources/WSR/OneTracker.xlsx",
    "Beeqom": "dataSources/WSR/OneTracker.xlsx",
    "Corporate Actions": "dataSources/WSR/OneTracker.xlsx",
    "HRIS": "dataSources/WSR/OneTracker.xlsx",
    "ICS": "dataSources/WSR/OneTracker.xlsx",
    "vEMS": "dataSources/WSR/OneTracker.xlsx",
    "Workday": "dataSources/WSR/OneTracker.xlsx",
    "FX Central": "dataSources/WSR/OneTracker.xlsx",
    "Mercatus": "dataSources/WSR/OneTracker.xlsx",
    "QA Smoke Test": "dataSources/WSR/OneTracker.xlsx",
}


@app.errorhandler(404)
def not_found(e):
    return render_template("accounts/404.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(
            username=form.username.data, password=form.password.data
        ).first()
        if user:
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash(
                "Login unsuccessful. Please check your username and password.", "danger"
            )

    return render_template("accounts/login.html", form=form)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    # if current_user.is_authenticated:
    #         return redirect(url_for('index'))
    choices=fileAssociate.keys()
    
    form = SignupForm()
    form.set_projects_choices([(project, project) for project in choices])

    if form.password.data != form.confirm_password.data:
        flash(
            "Password and confirm password do not match. Please try again.",
            "danger",
        )
        return redirect(url_for("signup"))
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", "danger")
            return redirect(url_for("signup"))

        try:
            new_user = User(
                username=form.username.data,
                password=form.password.data,
                department=form.department.data,
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Your account has been created! You can now log in.", "success")
            return redirect(url_for("login"))
        except IntegrityError:
            db.session.rollback()
            flash(
                "An error occurred while creating your account. Please try again.",
                "danger",
            )
            return redirect(url_for("signup"))

    return render_template("accounts/signup.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/home", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    return render_template("pages/index.html", userName=current_user.username)


@app.route("/home/dashboard", methods=["GET", "POST"])
@login_required
def Dashboard():
    summary_efforts_fromsheet = load_data(
        "dataSources/monthData/dashSummary.xlsx", "Efforts", 0, dat.now().month
    )

    summary_cost_fromsheet = load_data(
        "dataSources/monthData/dashSummary.xlsx", "Cost", 0, dat.now().month
    )

    summary_resource_fromsheet = load_data(
        "dataSources/monthData/dashSummary.xlsx", "Resource", 0, dat.now().month
    )
    decimal_places = 2
    summary_efforts_fromsheet = summary_efforts_fromsheet.round(decimal_places)
    summary_cost_fromsheet = summary_cost_fromsheet.round(decimal_places)
    summary_resource_fromsheet = summary_resource_fromsheet.round(decimal_places)

    summary_efforts_fromsheet = summary_efforts_fromsheet.set_index("Project")

    efforts_dict = summary_efforts_fromsheet.transpose().to_dict()
    cost_dict = summary_cost_fromsheet.to_dict()
    resource_dict = summary_resource_fromsheet.to_dict()

    efforts_chart_data = []
    cost_chart_data = []

    for month, values in efforts_dict.items():
        month_data = {"name": month, "data": values}
        efforts_chart_data.append(month_data)

    for month, values in cost_dict.items():
        month_data = {"name": month, "data": values}
        cost_chart_data.append(month_data)

    options_project = [entry["name"] for entry in efforts_chart_data]
    options_cost = [
        entry["name"] for entry in cost_chart_data if entry["name"] != "Project"
    ]

    if request.method == "POST" and "selected_project" in request.form:
        selected_option_project = request.form.get("selected_project")
        session["selected_project"] = selected_option_project

        selected_option_month = session["selected_cost"]

    if request.method == "POST" and "selected_cost" in request.form:
        selected_option_month = request.form.get("selected_cost")
        session["selected_cost"] = selected_option_month

        selected_option_project = session["selected_project"]

    if request.method == "GET":
        selected_option_project = options_project[0]
        session["selected_project"] = options_project[0]

        selected_option_month = options_cost[0]
        session["selected_cost"] = options_cost[0]

    filtered_data_efforts = [
        entry
        for entry in efforts_chart_data
        if entry["name"] == selected_option_project
    ]

    return render_template(
        "pages/dashboard.html",
        dropdown_project=options_project,
        dropdown_cost=options_cost,
        selected_project=selected_option_project,
        selected_month=selected_option_month,
        userName=current_user.username,
        getSplineChart1=SplineChart(
            chartName="SplineChart1",
            title="Total Efforts (Hrs.)",
            subtitle=f"Project : {selected_option_project}",
            max_width="624px",
            min_width="312px",
            height="600px",
            background_color="transparent",
            borderColor="black",
            lineColor="Crimson",
            xAxisTitle="Month",
            xAxisData=list(filtered_data_efforts[0]["data"].keys()),
            yAxisTitle="Efforts",
            yAxisData=list(filtered_data_efforts[0]["data"].values()),
            dataLabels_enabled="true",
            dataLabels_Color="black",

        ),
        getColumnChart1=ColumnChart(
            chartName="ColumnChart1",
            title="Total Efforts (Hrs.)",
            subtitle=f"Project : {selected_option_project}",
            max_width="624px",
            min_width="312px",
            height="600px",
            background_color="transparent",
            borderColor="black",
            lineColor="darkgreen",
            colorByPoint="false",
            xAxisTitle="Month",
            xAxisData=list(filtered_data_efforts[0]["data"].keys()),
            yAxisTitle="Efforts",
            yAxisData=list(filtered_data_efforts[0]["data"].values()),
            dataLabels_enabled="true",
            dataLabels_Color="white",
            dataLabels_font_size="12px",
            dataLabels_rotation=-90,
            dataLabels_align="right",
            dataLabels_padding=8,
        ),
        getBarChart1=BarChart(
            chartName="BarChart1",
            title="Cost Summary",
            subtitle=f"Month : {selected_option_month}",
            max_width="624px",
            min_width="312px",
            height="600px",
            background_color="transparent",
            borderColor="black",
            lineColor="darkblue",
            colorByPoint="false",
            xAxisTitle="Projects",
            xAxisData=list(cost_dict["Project"].values()),
            yAxisTitle="Cost",
            yAxisData=list(cost_dict[selected_option_month].values()),
            dataLabels_enabled="true",
            dataLabels_Color="yellow",
            dataLabels_font_size="13px",
        ),
        getBarChart2=BarChart(
            chartName="BarChart2",
            title="Resource Summary",
            subtitle=f"Month : {selected_option_month}",
            max_width="624px",
            min_width="312px",
            height="600px",
            background_color="transparent",
            borderColor="black",
            lineColor="darkorange",
            colorByPoint="false",
            xAxisTitle="Projects",
            xAxisData=list(resource_dict["Project"].values()),
            yAxisTitle="Resource",
            yAxisData=list(resource_dict[selected_option_month].values()),
            dataLabels_enabled="true",
            dataLabels_Color="black",
            dataLabels_font_size="13px",
        ),
    )


@app.route("/home/depdash", methods=["GET", "POST"])
@login_required
def depdash():
    efforts_chart_data = getChartData(
        "dataSources/monthData/dashSummary.xlsx", "Efforts", "Project"
    )
    cost_chart_data = getChartData(
        "dataSources/monthData/dashSummary.xlsx", "Cost", "Project"
    )
    resource_chart_data = getChartData(
        "dataSources/monthData/dashSummary.xlsx", "Resource", "Project"
    )

    options_project = [entry["name"] for entry in efforts_chart_data]

    if request.method == "POST":
        selected_option_project = request.form.get("selected_project")
        session["selected_project"] = selected_option_project

    if request.method == "GET":
        selected_option_project = options_project[0]
        session["selected_project"] = options_project[0]

    filtered_data_efforts = filterDataSummary(
        efforts_chart_data, selected_option_project
    )
    filtered_data_cost = filterDataSummary(cost_chart_data, selected_option_project)
    filtered_resource_cost = filterDataSummary(resource_chart_data, selected_option_project)

    return render_template(
        "pages/depdash.html",
        dropdown_project=options_project,
        selected_project=selected_option_project,
        userName=current_user.username,
        getColumnChart1=ColumnChart(
            chartName="ColumnChart1",
            title="Total Efforts (Hrs.)",
            subtitle=f"Project : {selected_option_project}",
            max_width="624px",
            min_width="312px",
            height="",
            background_color="transparent",
            borderColor="black",
            lineColor="darkblue",
            colorByPoint="false",
            xAxisTitle="Month",
            xAxisData=list(filtered_data_efforts[0]["data"].keys()),
            yAxisTitle="Efforts",
            yAxisData=list(filtered_data_efforts[0]["data"].values()),
            dataLabels_enabled="true",
            dataLabels_Color="white",
            dataLabels_font_size="12px",
            dataLabels_rotation=-90,
            dataLabels_align="right",
            dataLabels_padding=8,
        ),
        getColumnChart2=ColumnChart(
            chartName="ColumnChart2",
            title="Cost of Labor",
            subtitle=f"Project : {selected_option_project}",
            max_width="",
            min_width="",
            height="",
            background_color="transparent",
            borderColor="black",
            lineColor="darkgreen",
            colorByPoint="false",
            xAxisTitle="Month",
            xAxisData=list(filtered_data_cost[0]["data"].keys()),
            yAxisTitle="Cost",
            yAxisData=list(filtered_data_cost[0]["data"].values()),
            dataLabels_enabled="true",
            dataLabels_Color="white",
            dataLabels_font_size="12px",
            dataLabels_rotation=-90,
            dataLabels_align="right",
            dataLabels_padding=8,
        ),
        getSplineChart1=SplineChart(
            chartName="SplineChart1",
            title="QA Team Size",
            subtitle=f"Project : {selected_option_project}",
            max_width="624px",
            min_width="312px",
            height="",
            background_color="transparent",
            borderColor="black",
            lineColor="Crimson",
            xAxisTitle="Month",
            xAxisData=list(filtered_resource_cost[0]["data"].keys()),
            yAxisTitle="Team Size",
            yAxisData=list(filtered_resource_cost[0]["data"].values()),
            dataLabels_enabled="true",
            dataLabels_Color="black",
        ),
    )


@app.route("/home/mdash", methods=["GET", "POST"])
@login_required
def mdash():
    summary_efforts_fromsheet = load_data(
        "dataSources/monthData/dashSummary.xlsx", "Efforts", 0, dat.now().month
    )

    summary_cost_fromsheet = load_data(
        "dataSources/monthData/dashSummary.xlsx", "Cost", 0, dat.now().month
    )

    summary_resource_fromsheet = load_data(
        "dataSources/monthData/dashSummary.xlsx", "Resource", 0, dat.now().month
    )
    decimal_places = 2
    summary_efforts_fromsheet = summary_efforts_fromsheet.round(decimal_places)
    summary_cost_fromsheet = summary_cost_fromsheet.round(decimal_places)
    summary_resource_fromsheet = summary_resource_fromsheet.round(decimal_places)

    efforts_dict = summary_efforts_fromsheet.transpose().to_dict()
    cost_dict = summary_cost_fromsheet.to_dict()
    resource_dict = summary_resource_fromsheet.to_dict()

    efforts_chart_data = []
    cost_chart_data = []

    for month, values in efforts_dict.items():
        month_data = {"name": month, "data": values}
        efforts_chart_data.append(month_data)

    for month, values in cost_dict.items():
        month_data = {"name": month, "data": values}
        cost_chart_data.append(month_data)

    options_project = [entry["name"] for entry in efforts_chart_data]
    options_cost = [
        entry["name"] for entry in cost_chart_data if entry["name"] != "Project"
    ]

    if request.method == "POST" and "selected_project" in request.form:
        selected_option_project = request.form.get("selected_project")
        session["selected_project"] = selected_option_project

        selected_option_month = session["selected_cost"]

    if request.method == "POST" and "selected_cost" in request.form:
        selected_option_month = request.form.get("selected_cost")
        session["selected_cost"] = selected_option_month

        selected_option_project = session["selected_project"]

    if request.method == "GET":
        selected_option_project = options_project[0]
        session["selected_project"] = options_project[0]

        selected_option_month = options_cost[-1]
        session["selected_cost"] = options_cost[-1]

    efforts_list_dict = getRowResource(
        summary_efforts_fromsheet, ["QA Department"], selected_option_month
    )

    cost_per_dict = sum_columns_cost(cost_dict, selected_option_month)
    resource_per_dict = sum_columns_resource(resource_dict, selected_option_month)
    cost_list_dict = getRowResource(
        summary_cost_fromsheet,
        ["Total T&M", "Projected Monthly Cost"],
        selected_option_month,
    )
    resource_list_dict = getRowResource(
        summary_resource_fromsheet,
        ["Non Utilization", "QA Summary"],
        selected_option_month,
    )
    return render_template(
        "pages/mdash.html",
        dropdown_project=options_project,
        dropdown_cost=options_cost,
        selected_project=selected_option_project,
        selected_month=selected_option_month,
        userName=current_user.username,
        getColumnChart1=ColumnChart(
            chartName="ColumnChart1",
            title="Total Efforts (Hrs.)",
            subtitle=f"Month : {options_cost[0]} - {selected_option_month}",
            max_width="624px",
            min_width="312px",
            height="600px",
            background_color="transparent",
            borderColor="black",
            lineColor="black",
            colorByPoint="false",
            xAxisTitle="",
            xAxisData=efforts_list_dict["QA Department"]["keys"],
            yAxisTitle="Efforts",
            yAxisData=efforts_list_dict["QA Department"]["values"],
            dataLabels_enabled="true",
            dataLabels_Color="white",
            dataLabels_font_size="12px",
            dataLabels_rotation=-90,
            dataLabels_align="right",
            dataLabels_padding=8,
        ),
        getMultiLineChart1=MultiLineChart(
            chartName="MultiLineChart1",
            title="QA Team Size",
            subtitle=f"Month : {options_cost[0]} - {selected_option_month}",
            max_width="624px",
            min_width="312px",
            height="600px",
            background_color="transparent",
            borderColor="black",
            xAxisTitle="",
            xAxisData=resource_list_dict["Non Utilization"]["keys"],
            yAxisTitle="Team Size",
            yAxisName1="Non Utilization",
            yAxisData1=resource_list_dict["Non Utilization"]["values"],
            lineColor1="blue",
            yAxisName2="Team Size",
            yAxisData2=resource_list_dict["QA Summary"]["values"],
            lineColor2="orange",
            dataLabels_enabled="true",
            dataLabels_Color="black",
        ),
        getMultiColumnChart1=MultiColumnChart(
            chartName="MultiColumnChart1",
            title="Cost of Labor (Projected vs Actual)",
            subtitle=f"Month : {options_cost[0]} - {selected_option_month}",
            max_width="624px",
            min_width="312px",
            height="600px",
            background_color="transparent",
            borderColor="black",
            lineColor1="#001440",
            lineColor2="#DC582A",
            colorByPoint="false",
            xAxisTitle="",
            xAxisData=cost_list_dict["Total T&M"]["keys"],
            yAxisTitle="Efforts",
            yAxisData1=cost_list_dict["Total T&M"]["values"],
            yAxisData2=cost_list_dict["Projected Monthly Cost"]["values"],
            dataLabels_enabled="true",
            dataLabels_Color1="white",
            dataLabels_Color2="#001440",
            dataLabels_font_size="12px",
            dataLabels_rotation=-90,
            dataLabels_align="right",
            dataLabels_padding=8,
        ),
        getBarChart1=BarChart(
            chartName="BarChart1",
            title="Project Wise Cost Summary",
            subtitle=f"Month : {options_cost[0]} - {selected_option_month}",
            max_width="624px",
            min_width="312px",
            height="600px",
            background_color="transparent",
            borderColor="black",
            lineColor="black",
            colorByPoint="false",
            xAxisTitle="",
            xAxisData=list(cost_per_dict["Project"]),
            yAxisTitle="Cost",
            yAxisData=list(cost_per_dict["Total"]),
            dataLabels_enabled="true",
            dataLabels_Color="yellow",
            dataLabels_font_size="13px",
        ),
        getBarChart2=BarChart(
            chartName="BarChart2",
            title="Resource Management Summary",
            subtitle=f"Month : {options_cost[0]} - {selected_option_month}",
            max_width="624px",
            min_width="312px",
            height="600px",
            background_color="transparent",
            borderColor="black",
            lineColor="black",
            colorByPoint="true",
            xAxisTitle="",
            xAxisData=list(resource_per_dict["Project"]),
            yAxisTitle="Resource",
            yAxisData=list(resource_per_dict["Total"]),
            dataLabels_enabled="true",
            dataLabels_Color="yellow",
            dataLabels_font_size="13px",
        ),
    )


@app.route("/about")
@login_required
def about():
    dfHtml = ""
    return render_template("pages/about.html", dfHtml=dfHtml)





@app.route("/home/<template>", methods=["GET", "POST"])
@login_required
def pages(template):
    if template != "favicon.ico":
        if not template in fileAssociate.keys():
            return render_template("accounts/404.html")
    options_week = (
        getSheetNames(fileAssociate[template])
        if template != "favicon.ico"
        else getSheetNames(fileAssociate[list(fileAssociate.keys())[0]])
    )

    if request.method == "POST":
        selected_option = request.form.get("selected_option")
        session["selected_option"] = selected_option

    elif request.method == "GET":
        selected_option = options_week[0]
        session["selected_option"] = options_week[0]

    tables_fromsheet = (
        load_tables(fileAssociate[template], selected_option)
        if template != "favicon.ico"
        else load_tables(fileAssociate[list(fileAssociate.keys())[0]], selected_option)
    )

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


if __name__ == "__main__":
    app.run(debug=True)
