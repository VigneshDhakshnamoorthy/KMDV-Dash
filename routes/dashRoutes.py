from datetime import datetime
import math
from typing import Coroutine
from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required
import pandas as pd
from routes.enumLinks import ChartData, FileAssociate, getUserName
from utils.dataUtil import (
    add_missing_dates,
    add_missing_dates_project,
    filter_active_projects,
    filter_active_projects_df,
    filter_active_years,
    filter_data_by_rows,
    filter_full_data,
    filterDataSummary,
    getChartDataTotal,
    getDateNow,
    getMonth,
    getRowResource,
    getSheetNames,
    getSinceData,
    getSinceDataAvg,
    getSinceDataSum,
    getYearList,
    load_data,
    load_data_month_skip,
    load_full_data,
    load_tables,
    sum_columns,
    sum_columns_row,
    weekDays,
)

from utils.zynaCharts import (
    BarChart,
    ColumnChart,
    MultiColumnChart,
    MultiSplineChart,
    MultiSplineChart3,
    PieChart,
    SplineChart,
)
import asyncio
from asyncio import to_thread


month_today = 3
year_list = getYearList(month=month_today)

DashboardPage = Blueprint("DashboardPage", __name__, template_folder="templates")


@DashboardPage.route("/dashboard", methods=["GET", "POST"])
@login_required
async def Dashboard():
    summary_efforts_fromsheet = await to_thread(
        lambda: load_data(
            "dataSources/monthData/dashSummary.xlsx",
            "Efforts",
            0,
            getMonth(month=month_today),
        )
    )

    summary_cost_fromsheet = await to_thread(
        lambda: load_data(
            "dataSources/monthData/dashSummary.xlsx",
            "Cost",
            0,
            getMonth(month=month_today),
        )
    )

    summary_resource_fromsheet = await to_thread(
        lambda: load_data(
            "dataSources/monthData/dashSummary.xlsx",
            "Resource",
            0,
            getMonth(month=month_today),
        )
    )
    decimal_places = 3
    summary_efforts_fromsheet = await summary_efforts_fromsheet
    summary_efforts_fromsheet = summary_efforts_fromsheet.round(decimal_places)
    summary_cost_fromsheet = await summary_cost_fromsheet
    summary_cost_fromsheet = summary_cost_fromsheet.round(decimal_places)
    summary_resource_fromsheet = await summary_resource_fromsheet
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
        userName=getUserName(current_user),
        getSplineChart1=await SplineChart(
            chartName="SplineChart1",
            title="Total Efforts (Hrs.)",
            subtitle=f"Project : {selected_option_project}",
            max_width=ChartData.max_width.value,
            min_width=ChartData.min_width.value,
            height="",
            background_color=ChartData.background_color.value,
            borderColor=ChartData.borderColor.value,
            lineColor=ChartData.lineColor_spline.value,
            xAxisTitle="Month",
            xAxisData=list(filtered_data_efforts[0]["data"].keys()),
            yAxisTitle="Efforts",
            yAxisData=list(filtered_data_efforts[0]["data"].values()),
            dataLabels_enabled="true",
            dataLabels_format=ChartData.dataLabels_format_0f.value,
            dataLabels_Color="black",
            gridLineWidth=ChartData.gridLineWidth.value,
        ),
        getColumnChart1=await ColumnChart(
            chartName="ColumnChart1",
            title="Total Efforts (Hrs.)",
            subtitle=f"Project : {selected_option_project}",
            max_width=ChartData.max_width.value,
            min_width=ChartData.min_width.value,
            height="",
            background_color=ChartData.background_color.value,
            borderColor=ChartData.borderColor.value,
            lineColor=ChartData.lineColor_column.value,
            colorByPoint="false",
            xAxisTitle="Month",
            xAxisData=list(filtered_data_efforts[0]["data"].keys()),
            yAxisTitle="Efforts",
            yAxisData=list(filtered_data_efforts[0]["data"].values()),
            dataLabels_enabled="true",
            dataLabels_format=ChartData.dataLabels_format_0f.value,
            dataLabels_Color="black",
            dataLabels_font_size="12px",
            dataLabels_rotation=0,
            dataLabels_align="center",
            dataLabels_padding=0,
            gridLineWidth=ChartData.gridLineWidth.value,
        ),
        getBarChart1=await BarChart(
            chartName="BarChart1",
            title="Cost Summary",
            subtitle=f"Month : {selected_option_month}",
            max_width=ChartData.max_width.value,
            min_width=ChartData.min_width.value,
            height=ChartData.height.value,
            background_color=ChartData.background_color.value,
            borderColor=ChartData.borderColor.value,
            lineColor=ChartData.lineColor_bar.value,
            colorByPoint="false",
            xAxisTitle="Projects",
            xAxisData=list(cost_dict["Project"].values()),
            yAxisTitle="Cost",
            yAxisData=list(cost_dict[selected_option_month].values()),
            dataLabels_enabled="true",
            dataLabels_format=ChartData.dataLabels_format_m0f.value,
            dataLabels_Color="black",
            dataLabels_font_size="13px",
            gridLineWidth=ChartData.gridLineWidth.value,
        ),
        getBarChart2=await BarChart(
            chartName="BarChart2",
            title="Resource Summary",
            subtitle=f"Month : {selected_option_month}",
            max_width=ChartData.max_width.value,
            min_width=ChartData.min_width.value,
            height=ChartData.height.value,
            background_color=ChartData.background_color.value,
            borderColor=ChartData.borderColor.value,
            lineColor=ChartData.lineColor_bar.value,
            colorByPoint="false",
            xAxisTitle="Projects",
            xAxisData=list(resource_dict["Project"].values()),
            yAxisTitle="Resource",
            yAxisData=list(resource_dict[selected_option_month].values()),
            dataLabels_enabled="true",
            dataLabels_format=ChartData.dataLabels_format_1f.value,
            dataLabels_Color="black",
            dataLabels_font_size="13px",
            gridLineWidth=ChartData.gridLineWidth.value,
        ),
    )


@DashboardPage.route("/depdash/<project_name>/<project_year>", methods=["GET", "POST"])
@login_required
async def depdashdirect(project_name, project_year):

    project_name = project_name.upper()
    project_year = int(project_year)
    filtered_years = year_list
    if not project_name == "ALL":
        filtered_years = await to_thread(
            filter_active_years,
            project_name,
            year_list,
            "dataSources/monthData/dashSummary.xlsx",
            sheet_name="ActiveHistory",
        )
        filtered_years = await filtered_years

    print(filtered_years)
    project_year = (
        filtered_years[0] if project_year not in filtered_years else project_year
    )
    selected_option_year = project_year
    project_list = await to_thread(current_user.get_projects_list)

    project_list = await to_thread(
        filter_active_projects,
        project_list,
        project_year,
        "dataSources/monthData/dashSummary.xlsx",
        sheet_name="ActiveHistory",
    )

    project_list = await project_list
    project_list.append("All")
    if not project_name in project_list and project_name != "ALL":
        return render_template("accounts/wsrAuth.html")

    if request.method == "GET":
        selected_option_project = project_name
        session["selected_project"] = project_name
        selected_option_year = selected_option_year
        session["selected_year"] = selected_option_year

    if request.method == "POST" and "selected_year" in request.form:
        selected_option_year = request.form.get("selected_year")
        session["selected_year"] = selected_option_year

        selected_option_project = session["selected_project"]
        return redirect(
            url_for(
                "DashboardPage.depdashdirect",
                project_name=selected_option_project,
                project_year=selected_option_year,
            )
        )

    if request.method == "POST" and "selected_project" in request.form:
        selected_option_project = request.form.get("selected_project")
        session["selected_project"] = selected_option_project
        selected_option_year = session["selected_year"]
        return redirect(
            url_for(
                "DashboardPage.depdashdirect",
                project_name=selected_option_project,
                project_year=selected_option_year,
            )
        )

    efforts_chart_data = await to_thread(
        lambda: getChartDataTotal(
            filePath="dataSources/monthData/dashSummary.xlsx",
            sheetName="Efforts",
            set_index="Project",
            start=1,
            month=getMonth(
                int(selected_option_year), month=month_today, max=max(year_list)
            ),
            projects_list=project_list,
            year_selection=int(selected_option_year),
        )
    )
    cost_chart_data = await to_thread(
        lambda: getChartDataTotal(
            filePath="dataSources/monthData/dashSummary.xlsx",
            sheetName="Cost",
            set_index="Project",
            start=1,
            end=-2,
            month=getMonth(
                int(selected_option_year), month=month_today, max=max(year_list)
            ),
            projects_list=project_list,
            year_selection=int(selected_option_year),
        )
    )
    
    resource_chart_data = await to_thread(
        lambda: getChartDataTotal(
            filePath="dataSources/monthData/dashSummary.xlsx",
            sheetName="Resource",
            set_index="Project",
            start=1,
            end=-2,
            month=getMonth(
                int(selected_option_year), month=month_today, max=max(year_list)
            ),
            projects_list=project_list,
            year_selection=int(selected_option_year),
        )
    )
    efforts_chart_data = await efforts_chart_data
    cost_chart_data = await cost_chart_data
    resource_chart_data = await resource_chart_data

    filtered_data_efforts = await to_thread(
        lambda: filterDataSummary(efforts_chart_data, selected_option_project)
    )

    eff_data = add_missing_dates_project(filtered_data_efforts[0])

    filtered_data_cost = await to_thread(
        lambda: filterDataSummary(cost_chart_data, selected_option_project)
    )
    cost_data = add_missing_dates_project(filtered_data_cost[0])

    filtered_resource_cost = await to_thread(
        lambda: filterDataSummary(resource_chart_data, selected_option_project)
    )
    res_data = add_missing_dates_project(filtered_resource_cost[0])

    options_project = [entry["name"] for entry in efforts_chart_data]

    total_efforts = [
        value
        for value in list(filtered_data_efforts[0]["data"].values())
        if isinstance(value, (int, float)) and not math.isnan(value)
    ]
    total_cost = [
        value
        for value in list(filtered_data_cost[0]["data"].values())
        if isinstance(value, (int, float)) and not math.isnan(value)
    ]
    avg_team = [
        value
        for value in list(filtered_resource_cost[0]["data"].values())
        if isinstance(value, (int, float))
        and not math.isnan(float(value))
        and value > 0
    ]
    total_efforts = "{:0,.0f}".format(math.ceil(sum(total_efforts)))
    total_cost = "$ {:0,.0f}".format(math.ceil(sum(total_cost)))
    if len(avg_team) > 0:
        if float(sum(avg_team) / len(avg_team)) < 0.1:
            avg_team = "{:0,.2f}".format(sum(avg_team) / len(avg_team))
        else:
            avg_team = "{:0,.1f}".format(sum(avg_team) / len(avg_team))

    else:
        avg_team = 0

    wsr_bool = (not FileAssociate.get_value(session["selected_project"]) is None) and (
        int(selected_option_year) > 2022
    )

    return render_template(
        "pages/depdash.html",
        dropdown_project=options_project,
        dropdown_year=filtered_years,
        selected_project=selected_option_project,
        selected_year=int(selected_option_year),
        userName=getUserName(current_user),
        total_efforts=total_efforts,
        total_cost=total_cost,
        avg_team=avg_team,
        wsr_bool=wsr_bool,
        getColumnChart1=await ColumnChart(
            chartName="ColumnChart1",
            title="MONTHLY EFFORT (HRS.)",
            subtitle=f"PROJECT : {selected_option_project.replace('_',' ')} / {int(selected_option_year)}",
            max_width=ChartData.max_width.value,
            min_width=ChartData.min_width.value,
            height="",
            background_color=ChartData.background_color.value,
            borderColor=ChartData.borderColor.value,
            lineColor=ChartData.lineColor_column.value,
            colorByPoint="false",
            xAxisTitle="",
            xAxisData=list(eff_data["data"].keys()),
            yAxisTitle="EFFORT",
            yAxisData=list(eff_data["data"].values()),
            dataLabels_enabled="true",
            dataLabels_format=ChartData.dataLabels_format_0f.value,
            dataLabels_Color="black",
            dataLabels_font_size="12px",
            dataLabels_rotation=0,
            dataLabels_align="center",
            dataLabels_padding=0,
            gridLineWidth=ChartData.gridLineWidth.value,
        ),
        getColumnChart2=await ColumnChart(
            chartName="ColumnChart2",
            title="COST OF QA",
            subtitle=f"PROJECT : {selected_option_project.replace('_',' ')} / {int(selected_option_year)}",
            max_width=ChartData.max_width.value,
            min_width=ChartData.min_width.value,
            height="",
            background_color=ChartData.background_color.value,
            borderColor=ChartData.borderColor.value,
            lineColor=ChartData.lineColor_column.value,
            colorByPoint="false",
            xAxisTitle="",
            xAxisData=list(cost_data["data"].keys()),
            yAxisTitle="COST",
            yAxisData=list(cost_data["data"].values()),
            dataLabels_enabled="true",
            dataLabels_format=ChartData.dataLabels_format_m0f.value,
            dataLabels_Color="black",
            dataLabels_font_size="12px",
            dataLabels_rotation=0,
            dataLabels_align="center",
            dataLabels_padding=0,
            gridLineWidth=ChartData.gridLineWidth.value,
        ),
        getSplineChart1=await SplineChart(
            chartName="SplineChart1",
            title="UTILIZED TEAM",
            subtitle=f"PROJECT : {selected_option_project.replace('_',' ')} / {int(selected_option_year)}",
            max_width=ChartData.max_width.value,
            min_width=ChartData.min_width.value,
            height="",
            background_color=ChartData.background_color.value,
            borderColor=ChartData.borderColor.value,
            lineColor=ChartData.lineColor_spline.value,
            xAxisTitle="",
            xAxisData=list(res_data["data"].keys()),
            yAxisTitle="NO OF QA",
            yAxisData=list(res_data["data"].values()),
            dataLabels_enabled="true",
            dataLabels_format=ChartData.dataLabels_format_1f.value,
            dataLabels_Color="black",
            gridLineWidth=ChartData.gridLineWidth.value,
        ),
    )


@DashboardPage.route("/mdash", methods=["GET", "POST"])
@login_required
async def mdash():
    selected_option_year = year_list[0]
    if request.method == "POST" and "selected_year" in request.form:
        selected_option_year = request.form.get("selected_year")
        session["selected_year"] = selected_option_year

        selected_option_month = session["selected_month"]

    summary_efforts_fromsheet = await to_thread(
        lambda: load_data_month_skip(
            "dataSources/monthData/dashSummary.xlsx",
            "Efforts",
            0,
            getMonth(int(selected_option_year), month=month_today, max=max(year_list)),
            int(selected_option_year),
        )
    )

    summary_cost_fromsheet = await to_thread(
        lambda: load_data_month_skip(
            "dataSources/monthData/dashSummary.xlsx",
            "Cost",
            0,
            getMonth(int(selected_option_year), month=month_today, max=max(year_list)),
            int(selected_option_year),
        )
    )

    summary_department_fromsheet = await to_thread(
        lambda: load_data_month_skip(
            "dataSources/monthData/dashSummary.xlsx",
            "Department",
            0,
            getMonth(int(selected_option_year), month=month_today, max=max(year_list)),
            int(selected_option_year),
        )
    )

    summary_resource_fromsheet = await to_thread(
        lambda: load_data_month_skip(
            "dataSources/monthData/dashSummary.xlsx",
            "Resource",
            0,
            getMonth(int(selected_option_year), month=month_today, max=max(year_list)),
            int(selected_option_year),
        )
    )

    decimal_places = 2
    summary_efforts_fromsheet = await summary_efforts_fromsheet
    summary_efforts_fromsheet = summary_efforts_fromsheet.round(decimal_places)
    summary_cost_fromsheet = await summary_cost_fromsheet
    summary_cost_fromsheet = summary_cost_fromsheet.round(decimal_places)
    summary_resource_fromsheet = await summary_resource_fromsheet
    summary_resource_fromsheet = summary_resource_fromsheet.round(decimal_places)
    summary_department_fromsheet = await summary_department_fromsheet
    merged_df = pd.merge(
        summary_cost_fromsheet, summary_department_fromsheet, on="Project"
    )
    department_dfs = {}
    for department in merged_df["Department"].unique():
        department_dfs[department] = merged_df[
            merged_df["Department"] == department
        ].drop(columns=["Department"])

    efforts_dict = summary_efforts_fromsheet.transpose().to_dict()
    cost_dict = filter_data_by_rows(summary_cost_fromsheet, 1, -6).to_dict()
    dep_cost_dict = filter_data_by_rows(summary_cost_fromsheet, -8, "").to_dict()

    resource_dict_filtered = filter_data_by_rows(summary_resource_fromsheet, 2, -2)
    resource_dict_filtered = await filter_active_projects_df(
        resource_dict_filtered,
        selected_option_year,
        "dataSources/monthData/dashSummary.xlsx",
        sheet_name="ActiveHistory",
    )

    resource_dict_filtered = resource_dict_filtered.to_dict()

    efforts_chart_data = []
    cost_chart_data = []

    for month, values in efforts_dict.items():
        month_data = {"name": month, "data": values}
        efforts_chart_data.append(month_data)

    for month, values in cost_dict.items():
        month_data = {"name": month, "data": values}
        cost_chart_data.append(month_data)

    options_cost = [
        entry["name"] for entry in cost_chart_data if entry["name"] != "Project"
    ]

    selected_option_month = options_cost[-1]

    if request.method == "GET":
        selected_option_month = options_cost[-1]
        session["selected_month"] = options_cost[-1]

        selected_option_year = year_list[0]
        session["selected_year"] = year_list[0]

    efforts_list_dict = getRowResource(
        summary_efforts_fromsheet, ["QA Department"], selected_option_month
    )
    eff_data = add_missing_dates(efforts_list_dict)

    cost_per_dict = await to_thread(
        lambda: sum_columns_row(cost_dict, selected_option_month)
    )

    cost_dep_client_marketing = await to_thread(
        lambda: sum_columns(
            department_dfs["CLIENTS & MARKETING"], selected_option_month
        )
    )

    cost_dep_data_architecture = await to_thread(
        lambda: sum_columns(
            department_dfs["DATA & ARCHITECTURE"], selected_option_month
        )
    )
    cost_dep_finance = await to_thread(
        lambda: sum_columns(department_dfs["FINANCE"], selected_option_month)
    )
    cost_dep_investment = await to_thread(
        lambda: sum_columns(department_dfs["INVESTMENT"], selected_option_month)
    )
    cost_dep_business_operation = await to_thread(
        lambda: sum_columns(
            department_dfs["IT BUSINESS OPERATIONS"], selected_option_month
        )
    )

    dep_cost_per_dict = await to_thread(
        lambda: sum_columns_row(dep_cost_dict, selected_option_month)
    )

    cost_list_dict = await to_thread(
        lambda: getRowResource(
            summary_cost_fromsheet,
            ["Total T&M", "Projected Monthly Cost"],
            selected_option_month,
        )
    )
    cost_data = add_missing_dates(cost_list_dict)

    resource_list_dict = await to_thread(
        lambda: getRowResource(
            summary_resource_fromsheet,
            ["Non Utilization", "QA Summary", "QA Department"],
            selected_option_month,
        )
    )
    res_data = add_missing_dates(resource_list_dict)
    dep_cost_per_dict = [
        {"name": row["Project"], "y": row["Total"]}
        for index, row in dep_cost_per_dict.iterrows()
        if row["Total"] > 0
    ]
    projected_total = "$ {:0,.0f}".format(
        math.ceil(sum(cost_list_dict["Projected Monthly Cost"]["values"]))
    )
    actual_total = "$ {:0,.0f}".format(
        math.ceil(sum(cost_list_dict["Total T&M"]["values"]))
    )
    efforts_total = "{:0,.0f}".format(
        math.ceil(sum(efforts_list_dict["QA Department"]["values"]))
    )
    avg_team_size = "{:0,.1f}".format(
        sum(resource_list_dict["QA Summary"]["values"])
        / len(resource_list_dict["QA Summary"]["values"])
    )
    avg_team_size_util = "{:0,.1f}".format(
        sum(resource_list_dict["QA Department"]["values"])
        / len(resource_list_dict["QA Summary"]["values"])
    )
    avg_team_size_non_util = "{:0,.1f}".format(
        sum(resource_list_dict["Non Utilization"]["values"])
        / len(resource_list_dict["QA Summary"]["values"])
    )
    try:
        util_percent = "{:0,.0f}%".format(
            round(float(avg_team_size_util) / float(avg_team_size) * 100)
        )
    except ZeroDivisionError:
        util_percent = "0%"
    try:
        nonutil_percent = "{:0,.0f}%".format(
            round(float(avg_team_size_non_util) / float(avg_team_size) * 100)
        )
    except ZeroDivisionError:
        nonutil_percent = "0%"
    return render_template(
        "pages/mdash.html",
        dropdown_month=options_cost,
        dropdown_year=year_list,
        selected_month=selected_option_month,
        selected_year=int(selected_option_year),
        userName=getUserName(current_user),
        projected_total=projected_total,
        actual_total=actual_total,
        efforts_total=efforts_total,
        avg_team_size=avg_team_size,
        avg_team_size_util=avg_team_size_util,
        avg_team_size_non_util=avg_team_size_non_util,
        util_percent=util_percent,
        nonutil_percent=nonutil_percent,
        selected_project="Master Dashboard",
        getColumnChart1=await ColumnChart(
            chartName="ColumnChart1",
            title="MONTHLY EFFORT (HRS.)",
            subtitle=f"Month : {options_cost[0]} - {selected_option_month}",
            max_width=ChartData.max_width.value,
            min_width=ChartData.min_width.value,
            height=ChartData.height.value,
            background_color=ChartData.background_color.value,
            borderColor=ChartData.borderColor.value,
            lineColor=ChartData.lineColor_column.value,
            colorByPoint="false",
            xAxisTitle="",
            xAxisData=eff_data["QA Department"]["keys"],
            yAxisTitle="EFFORT",
            yAxisData=eff_data["QA Department"]["values"],
            dataLabels_enabled="true",
            dataLabels_format=ChartData.dataLabels_format_0f.value,
            dataLabels_Color="black",
            dataLabels_font_size="12px",
            dataLabels_rotation=0,
            dataLabels_align="center",
            dataLabels_padding=0,
            gridLineWidth=ChartData.gridLineWidth.value,
        ),
        getMultiLineChart1=await MultiSplineChart3(
            chartName="MultiLineChart1",
            title="QA TEAM SIZE",
            subtitle=f"Month : {options_cost[0]} - {selected_option_month}",
            max_width=ChartData.max_width.value,
            min_width=ChartData.min_width.value,
            height=ChartData.height.value,
            background_color=ChartData.background_color.value,
            borderColor=ChartData.borderColor.value,
            xAxisTitle="",
            xAxisData=res_data["Non Utilization"]["keys"],
            yAxisTitle="NO OF QA",
            yAxisName1="Non Utilization",
            yAxisData1=res_data["Non Utilization"]["values"],
            lineColor1=ChartData.lineColor_spline2.value,
            yAxisName2="Utilization",
            yAxisData2=res_data["QA Department"]["values"],
            lineColor2=ChartData.lineColor_bar.value,
            yAxisName3="Team Size",
            yAxisData3=res_data["QA Summary"]["values"],
            lineColor3=ChartData.lineColor_column.value,
            dataLabels_enabled="true",
            dataLabels_format=ChartData.dataLabels_format_1f.value,
            dataLabels_Color="black",
            gridLineWidth=ChartData.gridLineWidth.value,
            legend="true",
        ),
        getMultiColumnChart1=await MultiColumnChart(
            chartName="MultiColumnChart1",
            title="COST OF QA (PROJECTED vs ACTUAL)",
            subtitle=f"Month : {options_cost[0]} - {selected_option_month}",
            max_width=ChartData.max_width.value,
            min_width=ChartData.min_width.value,
            height=ChartData.height.value,
            background_color=ChartData.background_color.value,
            borderColor=ChartData.borderColor.value,
            lineColor1=ChartData.lineColor_column.value,
            lineColor2=ChartData.lineColor_bar.value,
            colorByPoint="false",
            xAxisTitle="",
            xAxisData=cost_data["Total T&M"]["keys"],
            yAxisTitle="$ COST",
            yAxisName1="Projected",
            yAxisData1=cost_data["Projected Monthly Cost"]["values"],
            yAxisName2="Actual",
            yAxisData2=cost_data["Total T&M"]["values"],
            dataLabels_enabled="true",
            dataLabels_format=ChartData.dataLabels_format_m0f.value,
            dataLabels_Color1="black",
            dataLabels_Color2="black",
            dataLabels_font_size="12px",
            dataLabels_rotation=0,
            dataLabels_align="center",
            dataLabels_padding=0,
            gridLineWidth=ChartData.gridLineWidth.value,
            legend="true",
        ),
        getBarChart4=await BarChart(
            chartName="BarChart4",
            title="CLIENTS & MARKETING COST SUMMARY",
            subtitle=f"Month : {options_cost[0]} - {selected_option_month}",
            max_width=ChartData.max_width.value,
            min_width=ChartData.min_width.value,
            height=ChartData.height.value,
            background_color=ChartData.background_color.value,
            borderColor=ChartData.borderColor.value,
            lineColor=ChartData.line_clients_marketing.value,
            colorByPoint="false",
            xAxisTitle="",
            xAxisData=list(cost_dep_client_marketing["Project"]),
            yAxisTitle="$ COST",
            yAxisData=list(cost_dep_client_marketing["Total"]),
            dataLabels_enabled="true",
            dataLabels_format=ChartData.dataLabels_format_m0f.value,
            dataLabels_Color="black",
            dataLabels_font_size="13px",
            gridLineWidth=ChartData.gridLineWidth.value,
        ),
        getBarChart5=await BarChart(
            chartName="BarChart5",
            title="DATA & ARCHITECTURE COST SUMMARY",
            subtitle=f"Month : {options_cost[0]} - {selected_option_month}",
            max_width=ChartData.max_width.value,
            min_width=ChartData.min_width.value,
            height=ChartData.height.value,
            background_color=ChartData.background_color.value,
            borderColor=ChartData.borderColor.value,
            lineColor=ChartData.line_data_architecture.value,
            colorByPoint="false",
            xAxisTitle="",
            xAxisData=list(cost_dep_data_architecture["Project"]),
            yAxisTitle="$ COST",
            yAxisData=list(cost_dep_data_architecture["Total"]),
            dataLabels_enabled="true",
            dataLabels_format=ChartData.dataLabels_format_m0f.value,
            dataLabels_Color="black",
            dataLabels_font_size="13px",
            gridLineWidth=ChartData.gridLineWidth.value,
        ),
        getBarChart6=await BarChart(
            chartName="BarChart6",
            title="FINANCE COST SUMMARY",
            subtitle=f"Month : {options_cost[0]} - {selected_option_month}",
            max_width=ChartData.max_width.value,
            min_width=ChartData.min_width.value,
            height=ChartData.height.value,
            background_color=ChartData.background_color.value,
            borderColor=ChartData.borderColor.value,
            lineColor=ChartData.line_finance.value,
            colorByPoint="false",
            xAxisTitle="",
            xAxisData=list(cost_dep_finance["Project"]),
            yAxisTitle="$ COST",
            yAxisData=list(cost_dep_finance["Total"]),
            dataLabels_enabled="true",
            dataLabels_format=ChartData.dataLabels_format_m0f.value,
            dataLabels_Color="black",
            dataLabels_font_size="13px",
            gridLineWidth=ChartData.gridLineWidth.value,
        ),
        getBarChart7=await BarChart(
            chartName="BarChart7",
            title="INVESTMENT COST SUMMARY",
            subtitle=f"Month : {options_cost[0]} - {selected_option_month}",
            max_width=ChartData.max_width.value,
            min_width=ChartData.min_width.value,
            height=ChartData.height.value,
            background_color=ChartData.background_color.value,
            borderColor=ChartData.borderColor.value,
            lineColor=ChartData.line_investment.value,
            colorByPoint="false",
            xAxisTitle="",
            xAxisData=list(cost_dep_investment["Project"]),
            yAxisTitle="$ COST",
            yAxisData=list(cost_dep_investment["Total"]),
            dataLabels_enabled="true",
            dataLabels_format=ChartData.dataLabels_format_m0f.value,
            dataLabels_Color="black",
            dataLabels_font_size="13px",
            gridLineWidth=ChartData.gridLineWidth.value,
        ),
        getBarChart8=await BarChart(
            chartName="BarChart8",
            title="IT BUSINESS OPERATIONS COST SUMMARY",
            subtitle=f"Month : {options_cost[0]} - {selected_option_month}",
            max_width=ChartData.max_width.value,
            min_width=ChartData.min_width.value,
            height=ChartData.height.value,
            background_color=ChartData.background_color.value,
            borderColor=ChartData.borderColor.value,
            lineColor=ChartData.line_it_business_operations.value,
            colorByPoint="false",
            xAxisTitle="",
            xAxisData=list(cost_dep_business_operation["Project"]),
            yAxisTitle="$ COST",
            yAxisData=list(cost_dep_business_operation["Total"]),
            dataLabels_enabled="true",
            dataLabels_format=ChartData.dataLabels_format_m0f.value,
            dataLabels_Color="black",
            dataLabels_font_size="13px",
            gridLineWidth=ChartData.gridLineWidth.value,
        ),
        getPieChart1=await PieChart(
            chartName="pie2",
            title="DEPARTMENTS COST SUMMARY",
            subtitle=f"Month : {options_cost[0]} - {selected_option_month}",
            max_width=ChartData.max_width.value,
            min_width=ChartData.min_width.value,
            height=ChartData.height.value,
            background_color=ChartData.background_color.value,
            borderColor=ChartData.borderColor.value,
            colorByPoint="true",
            dataLabels_enabled="true",
            dataLabels_format=ChartData.dataLabels_format_m0f.value,
            dataLabels_font_size="11px",
            series_name="Value",
            series_data=dep_cost_per_dict,
        ),
        getBarChart3=await BarChart(
            chartName="BarChart3",
            title="RESOURCE MANAGEMENT SUMMARY",
            subtitle=f"Month : {selected_option_month}",
            max_width=ChartData.max_width.value,
            min_width=ChartData.min_width.value,
            height=ChartData.height.value,
            background_color=ChartData.background_color.value,
            borderColor=ChartData.borderColor.value,
            lineColor=ChartData.lineColor_bar.value,
            colorByPoint="false",
            xAxisTitle="",
            xAxisData=list(resource_dict_filtered["Project"].values()),
            yAxisTitle="NO OF QA",
            yAxisData=list(resource_dict_filtered[selected_option_month].values()),
            dataLabels_enabled="true",
            dataLabels_format=ChartData.dataLabels_format_1f.value,
            dataLabels_Color="black",
            dataLabels_font_size="13px",
            gridLineWidth=ChartData.gridLineWidth.value,
        ),
    )


@DashboardPage.route("/depmaster", methods=["GET", "POST"])
@login_required
async def depmaster_land():
    return redirect(
        url_for(
            "DashboardPage.depmaster",
            project_name="ALL",
            project_year=year_list[0],
        )
    )


@DashboardPage.route(
    "/depmaster/<project_name>/<project_year>", methods=["GET", "POST"]
)
@login_required
async def depmaster(project_name:str, project_year:str):
    project_name = project_name.upper()
    project_year:int = int(project_year)
    filtered_years: list[int] = year_list
    if not project_name == "ALL":
        filtered_years = await to_thread(
            filter_active_years,
            project_name,
            year_list,
            "dataSources/monthData/dashSummary.xlsx",
            sheet_name="ActiveHistory",
        )
        filtered_years = await filtered_years

    project_year = (
        filtered_years[0] if project_year not in filtered_years else project_year
    )
    selected_option_year:int = project_year
    user_project_list = await to_thread(current_user.get_projects_list)
    project_list = user_project_list

    project_list:Coroutine[list] = await to_thread(
        filter_active_projects,
        project_list,
        project_year,
        "dataSources/monthData/dashSummary.xlsx",
        sheet_name="ActiveHistory",
    )

    project_list:list[str] = await project_list
    project_list.append("All")
    if not project_name in project_list and project_name != "ALL":
        return render_template("accounts/wsrAuth.html")

    if request.method == "GET":
        selected_option_project: str = project_name
        session["selected_project"] = project_name
        selected_option_year = selected_option_year
        session["selected_year"] = selected_option_year

    if request.method == "POST" and "selected_year" in request.form:
        selected_option_year = request.form.get("selected_year")
        session["selected_year"] = selected_option_year

        selected_option_project = session["selected_project"]
        return redirect(
            url_for(
                "DashboardPage.depmaster",
                project_name=project_name,
                project_year=selected_option_year,
            )
        )

    if request.method == "POST" and "selected_project" in request.form:
        selected_option_project = request.form.get("selected_project")
        session["selected_project"] = selected_option_project
        selected_option_year = session["selected_year"]
        return redirect(
            url_for(
                "DashboardPage.depmaster",
                project_name=selected_option_project,
                project_year=selected_option_year,
            )
        )

    efforts_chart_data:Coroutine[list[dict]] = await to_thread(
        lambda: getChartDataTotal(
            filePath="dataSources/monthData/dashSummary.xlsx",
            sheetName="Efforts",
            set_index="Project",
            start=1,
            month=getMonth(
                int(selected_option_year), month=month_today, max=max(year_list)
            ),
            projects_list=project_list,
            year_selection=int(selected_option_year),
        )
    )
    cost_chart_data:Coroutine[list[dict]] = await to_thread(
        lambda: getChartDataTotal(
            filePath="dataSources/monthData/dashSummary.xlsx",
            sheetName="Cost",
            set_index="Project",
            start=1,
            end=-2,
            month=getMonth(
                int(selected_option_year), month=month_today, max=max(year_list)
            ),
            projects_list=project_list,
            year_selection=int(selected_option_year),
        )
    )

    resource_chart_data:Coroutine[list[dict]] = await to_thread(
        lambda: getChartDataTotal(
            filePath="dataSources/monthData/dashSummary.xlsx",
            sheetName="Resource",
            set_index="Project",
            start=1,
            end=-2,
            month=getMonth(
                int(selected_option_year), month=month_today, max=max(year_list)
            ),
            projects_list=project_list,
            year_selection=int(selected_option_year),
        )
    )
    bug_chart_data:Coroutine[list[dict]] = await to_thread(
        lambda: getChartDataTotal(
            filePath="dataSources/monthData/dashSummary.xlsx",
            sheetName="Bug",
            set_index="Project",
            start=1,
            month=getMonth(
                int(selected_option_year), month=month_today, max=max(year_list)
            ),
            projects_list=project_list,
            year_selection=int(selected_option_year),
        )
    )
    execution_chart_data:Coroutine[list[dict]] = await to_thread(
        lambda: getChartDataTotal(
            filePath="dataSources/monthData/dashSummary.xlsx",
            sheetName="Execution",
            set_index="Project",
            start=1,
            month=getMonth(
                int(selected_option_year), month=month_today, max=max(year_list)
            ),
            projects_list=project_list,
            year_selection=int(selected_option_year),
        )
    )
    efforts_chart_data:list[dict] = await efforts_chart_data
    period = list(efforts_chart_data[0]['data'].keys())
    cost_chart_data:list[dict] = await cost_chart_data
    resource_chart_data:list[dict] = await resource_chart_data
    bug_chart_data:list[dict] = await bug_chart_data
    execution_chart_data:list[dict] = await execution_chart_data
    options_cost:list = [
        entry["name"] for entry in cost_chart_data if entry["name"] != "Project"
    ]

    selected_option_month:str = options_cost[-1]
    totals:dict = {}
    for entry in cost_chart_data:
        name = entry["name"]
        data = entry["data"]
        for key, value in data.items():
            if pd.isna(value):
                data[key] = 0
        if project_name == "ALL":
            if name != "ALL":
                total = sum(data.values())
                totals[name.replace("_", " ")] = total
        else:
            if name == project_name:
                total = sum(data.values())
                totals[name.replace("_", " ")] = total

    totals = {k: v if not pd.isna(v) else 0 for k, v in totals.items()}

    dep_cost_per_dict = [{"name": key, "y": value} for key, value in totals.items()]
    filtered_data_efforts = await to_thread(
        lambda: filterDataSummary(efforts_chart_data, selected_option_project)
    )

    eff_data = add_missing_dates_project(filtered_data_efforts[0])

    filtered_data_cost = await to_thread(
        lambda: filterDataSummary(cost_chart_data, selected_option_project)
    )
    cost_data = add_missing_dates_project(filtered_data_cost[0])

    filtered_resource_cost = await to_thread(
        lambda: filterDataSummary(resource_chart_data, selected_option_project)
    )
    res_data = add_missing_dates_project(filtered_resource_cost[0])

    filtered_data_bug = await to_thread(
        lambda: filterDataSummary(bug_chart_data, selected_option_project)
    )
    bug_data = add_missing_dates_project(filtered_data_bug[0])

    filtered_data_execution = await to_thread(
        lambda: filterDataSummary(execution_chart_data, selected_option_project)
    )
    execution_data = add_missing_dates_project(filtered_data_execution[0])

    options_project = [entry["name"] for entry in efforts_chart_data]

    total_efforts = [
        value
        for value in list(filtered_data_efforts[0]["data"].values())
        if isinstance(value, (int, float)) and not math.isnan(value)
    ]
    total_cost = [
        value
        for value in list(filtered_data_cost[0]["data"].values())
        if isinstance(value, (int, float)) and not math.isnan(value)
    ]

    avg_team = [
        value
        for value in list(filtered_resource_cost[0]["data"].values())
        if isinstance(value, (int, float))
        and not math.isnan(float(value))
        and value > 0
    ]
    total_efforts = "{:0,.0f}".format(math.ceil(sum(total_efforts)))
    total_cost = "$ {:0,.0f}".format(math.ceil(sum(total_cost)))

    if len(avg_team) > 0:
        if float(sum(avg_team) / len(avg_team)) < 0.1:
            avg_team = "{:0,.2f}".format(sum(avg_team) / len(avg_team))
        else:
            avg_team = "{:0,.1f}".format(sum(avg_team) / len(avg_team))

    else:
        avg_team = 0

    wsr_bool = (not FileAssociate.get_value(session["selected_project"]) is None) and (
        int(selected_option_year) > 2022
    )
    end_month = getMonth(
        int(selected_option_year), month=month_today, max=max(year_list)
    )
    if project_year < max(year_list):
        end_month = ((project_year - min(year_list)+1)*12)+1

    efforts_since_fromsheet = await asyncio.to_thread(
        getSinceDataSum,"Efforts",end_month,project_name, user_project_list
    )
    efforts_since = "{:0,.0f}".format(await efforts_since_fromsheet)
    cost_since_fromsheet = await asyncio.to_thread(
        getSinceDataSum,"Cost",end_month,project_name, user_project_list
    )
    cost_since = "$ {:0,.0f}".format(await cost_since_fromsheet)
    resource_since_fromsheet = await asyncio.to_thread(
        getSinceDataAvg,"Resource",end_month,project_name, user_project_list
    )
    resource_since: str = "{:0,.1f}".format(await resource_since_fromsheet)
    
    project_info_fromsheet = await asyncio.to_thread(
        load_full_data, "dataSources/monthData/dashSummary.xlsx", "Department"
    )
    full_wsr_since_info_fromsheet = await asyncio.to_thread(
        load_data, "dataSources/monthData/dashSummary.xlsx", "WSR-Copy", 11, 21
    )
    full_wsr_info_fromsheet = await asyncio.to_thread(
        load_data, "dataSources/monthData/dashSummary.xlsx", "WSR-Copy", 0, 10
    )
    automation_percentage_fromsheet = await asyncio.to_thread(
        load_full_data,
        "dataSources/monthData/dashSummary.xlsx",
        "Automation Percentage",
    )
    project_info_fromsheet = await project_info_fromsheet
    full_wsr_since_info_fromsheet = await full_wsr_since_info_fromsheet
    full_wsr_info_fromsheet = await full_wsr_info_fromsheet

    wsr_since_info_fromsheet = full_wsr_since_info_fromsheet[
        (full_wsr_since_info_fromsheet["Year"] == project_year)
        & full_wsr_since_info_fromsheet["Project"].isin(user_project_list)
    ]
    wsr_info_fromsheet = full_wsr_info_fromsheet[
        (full_wsr_info_fromsheet["Year."] == project_year)
        & full_wsr_info_fromsheet["Project."].isin(project_list)
    ]

    wsr_since_info_fromsheet = wsr_since_info_fromsheet.drop(columns=["Year"])
    wsr_since_info_fromsheet["Automation coverage"] = wsr_since_info_fromsheet[
        "Automation coverage"
    ].apply(lambda x: "{:.0f}%".format(x * 100))
    if not project_name == "ALL":
        wsr_since_info_fromsheet = wsr_since_info_fromsheet[
            wsr_since_info_fromsheet["Project"] == project_name
        ]
        wsr_info_fromsheet = wsr_info_fromsheet[
            wsr_info_fromsheet["Project."] == project_name
        ]

    total_bug_qa = "{:0,.0f}".format(
        math.ceil(sum(wsr_info_fromsheet["Bugs identified. QA"]))
    )
    total_bug_uat = "{:0,.0f}".format(
        math.ceil(sum(wsr_info_fromsheet["Bugs identified. UAT"]))
    )
    total_bug_prod = "{:0,.0f}".format(
        math.ceil(sum(wsr_info_fromsheet["Bugs identified. PROD"]))
    )

    total_bug_qa_inception = "{:0,.0f}".format(
        math.ceil(sum(wsr_since_info_fromsheet["Bugs identified QA"]))
    )
    total_bug_uat_inception = "{:0,.0f}".format(
        math.ceil(sum(wsr_since_info_fromsheet["Bugs identified UAT"]))
    )
    total_bug_prod_inception = "{:0,.0f}".format(
        math.ceil(sum(wsr_since_info_fromsheet["Bugs identified PROD"]))
    )

    total_manual_execution = sum(wsr_info_fromsheet["Manual test cases conducted."])
    total_automation_execution = sum(
        wsr_info_fromsheet["Automation test cases processed."]
    )
    total_execution = "{:0,.0f}".format(
        total_manual_execution + total_automation_execution
    )

    total_manual_execution_inception = sum(
        wsr_since_info_fromsheet["Manual test cases conducted"]
    )
    total_automation_execution_inception = sum(
        wsr_since_info_fromsheet["Automation test cases processed"]
    )
    total_execution_inception = "{:0,.0f}".format(
        total_manual_execution_inception + total_automation_execution_inception
    )

    total_manual_testcase = sum(wsr_info_fromsheet["Manual test cases created."])
    total_automation_testcase = sum(
        wsr_info_fromsheet["Automation test cases created."]
    )
    total_automation_percentage = (
        (total_automation_testcase / total_manual_testcase) * 100
        if not total_manual_testcase == 0
        else 0
    )
    total_automation_percentage = (
        100
        if total_automation_percentage > 100
        else (
            100
            if total_automation_testcase > total_manual_testcase
            else total_automation_percentage
        )
    )
    total_automation_percentage = "{:0,.0f}%".format(total_automation_percentage)
    # total_automation_percentage = "{:0,.0f}%".format((sum(wsr_info_fromsheet["Automation coverage."]) / len(wsr_info_fromsheet["Automation coverage."]))*100)
    total_testcase = "{:0,.0f}".format(
        total_manual_testcase + total_automation_testcase
    )
    total_automation_testcase = "{:0,.0f}".format(total_automation_testcase)
    total_manual_testcase = "{:0,.0f}".format(total_manual_testcase)

    total_manual_testcase_inception = sum(
        wsr_since_info_fromsheet["Manual test cases created"]
    )
    total_automation_testcase_inception = sum(
        wsr_since_info_fromsheet["Automation test cases created"]
    )
    total_automation_percentage_inception = (
        (total_automation_testcase_inception / total_manual_testcase_inception) * 100
        if not total_manual_testcase_inception == 0
        else 0
    )
    total_automation_percentage_inception = (
        100
        if total_automation_percentage_inception > 100
        else (
            100
            if total_automation_testcase_inception > total_manual_testcase_inception
            else total_automation_percentage_inception
        )
    )
    total_automation_percentage_inception = "{:0,.0f}%".format(
        total_automation_percentage_inception
    )
    total_testcase_inception = "{:0,.0f}".format(
        total_manual_testcase_inception + total_automation_testcase_inception
    )
    total_automation_testcase_inception = "{:0,.0f}".format(
        total_automation_testcase_inception
    )
    total_manual_testcase_inception = "{:0,.0f}".format(total_manual_testcase_inception)

    wsr_since_info_fromsheet["Project"] = wsr_since_info_fromsheet[
        "Project"
    ].str.replace("_", " ")
    automation_percentage_fromsheet = await automation_percentage_fromsheet
    automation_percentage_fromsheet = automation_percentage_fromsheet[
        automation_percentage_fromsheet["Project"].isin(project_list)
    ]
    automation_percentage_fromsheet.set_index("Project", inplace=True)
    class_table = "w-auto small"
    if project_name == "ALL":
        automation_percentage = automation_percentage_fromsheet[
            str(project_year)
        ].mean()
    else:
        automation_percentage = automation_percentage_fromsheet.loc[
            project_name, str(project_year)
        ]
        if "nan" in str(automation_percentage):
            automation_percentage = 0
    project_info = project_info_fromsheet.loc[
        project_info_fromsheet["Project"] == selected_option_project
    ]
    project_status, department, it_manager, qa_spoc, start_date = "", "", "", "", ""
    if not project_info.empty:
        project_status = project_info["Status"].values[0]
        department = project_info["Department"].values[0]
        it_manager = project_info["IT Manager"].values[0]
        qa_spoc = project_info["QA SPOC"].values[0]
        start_date = project_info["START DATE"].values[0]
        start_date = pd.to_datetime(start_date).strftime("%d %b %Y")
    
    return render_template(
        "pages/masterdep.html",
        dropdown_project=options_project,
        dropdown_year=filtered_years,
        selected_project=selected_option_project,
        selected_year=int(selected_option_year),
        time_duration = f"{period[0]} - {period[-1]}",
        userName=getUserName(current_user),
        total_efforts=total_efforts,
        total_cost=total_cost,
        total_bug_qa=total_bug_qa,
        total_bug_uat=total_bug_uat,
        total_bug_prod=total_bug_prod,
        total_bug_qa_inception=total_bug_qa_inception,
        total_bug_uat_inception=total_bug_uat_inception,
        total_bug_prod_inception=total_bug_prod_inception,
        total_execution=total_execution,
        total_execution_inception=total_execution_inception,
        automation_percentage=automation_percentage,
        avg_team=avg_team,
        wsr_bool=wsr_bool,
        project_status=project_status,
        department=department,
        it_manager=it_manager,
        qa_spoc=qa_spoc,
        start_date=start_date,
        efforts_since=efforts_since,
        cost_since=cost_since,
        resource_since=resource_since,
        total_automation_testcase=total_automation_testcase,
        total_manual_testcase=total_manual_testcase,
        total_automation_percentage=total_automation_percentage,
        total_automation_testcase_inception=total_automation_testcase_inception,
        total_manual_testcase_inception=total_manual_testcase_inception,
        total_automation_percentage_inception=total_automation_percentage_inception,
        wsr_info_fromsheet=wsr_since_info_fromsheet.to_html(
            classes=f"table table-bordered table-hover {class_table}", index=False
        ),
        getColumnChart1=await ColumnChart(
            chartName="ColumnChart1",
            title="ANNUAL EFFORT (HRS.)",
            subtitle=f"{selected_option_project.replace('_', ' ') + ' / ' if selected_option_project != 'ALL' else ''}{int(selected_option_year)}",
            max_width=ChartData.max_width.value,
            min_width=ChartData.min_width.value,
            height="",
            background_color=ChartData.background_color.value,
            borderColor=ChartData.borderColor.value,
            lineColor=ChartData.lineColor_column.value,
            colorByPoint="false",
            xAxisTitle="",
            xAxisData=list(eff_data["data"].keys()),
            yAxisTitle="EFFORT",
            yAxisData=list(eff_data["data"].values()),
            dataLabels_enabled="true",
            dataLabels_format=ChartData.dataLabels_format_0f.value,
            dataLabels_Color="black",
            dataLabels_font_size="12px",
            dataLabels_rotation=0,
            dataLabels_align="center",
            dataLabels_padding=0,
            gridLineWidth=ChartData.gridLineWidth.value,
        ),
        getColumnChart2=await ColumnChart(
            chartName="ColumnChart2",
            title="COST OF QA",
            subtitle=f"{selected_option_project.replace('_', ' ') + ' / ' if selected_option_project != 'ALL' else ''}{int(selected_option_year)}",
            max_width=ChartData.max_width.value,
            min_width=ChartData.min_width.value,
            height=ChartData.height.value,
            background_color=ChartData.background_color.value,
            borderColor=ChartData.borderColor.value,
            lineColor=ChartData.cost_column.value,
            colorByPoint="false",
            xAxisTitle="",
            xAxisData=list(cost_data["data"].keys()),
            yAxisTitle="COST",
            yAxisData=list(cost_data["data"].values()),
            dataLabels_enabled="true",
            dataLabels_format=ChartData.dataLabels_format_m0f.value,
            dataLabels_Color="black",
            dataLabels_font_size="12px",
            dataLabels_rotation=0,
            dataLabels_align="center",
            dataLabels_padding=0,
            gridLineWidth=ChartData.gridLineWidth.value,
        ),
        getColumnChart3=await ColumnChart(
            chartName="ColumnChart3",
            title="BUGS REPORTED - QA",
            subtitle=f"{selected_option_project.replace('_', ' ') + ' / ' if selected_option_project != 'ALL' else ''}{int(selected_option_year)}",
            max_width=ChartData.max_width.value,
            min_width=ChartData.min_width.value,
            height="",
            background_color=ChartData.background_color.value,
            borderColor=ChartData.borderColor.value,
            lineColor=ChartData.bug_column.value,
            colorByPoint="false",
            xAxisTitle="",
            xAxisData=list(bug_data["data"].keys()),
            yAxisTitle="BUGS",
            yAxisData=list(bug_data["data"].values()),
            dataLabels_enabled="true",
            dataLabels_format=ChartData.dataLabels_format_0f.value,
            dataLabels_Color="black",
            dataLabels_font_size="12px",
            dataLabels_rotation=0,
            dataLabels_align="center",
            dataLabels_padding=0,
            gridLineWidth=ChartData.gridLineWidth.value,
        ),
        getSplineChart1=await SplineChart(
            chartName="SplineChart1",
            title="UTILIZED TEAM",
            subtitle=f"{selected_option_project.replace('_', ' ') + ' / ' if selected_option_project != 'ALL' else ''}{int(selected_option_year)}",
            max_width=ChartData.max_width.value,
            min_width=ChartData.min_width.value,
            height="",
            background_color=ChartData.background_color.value,
            borderColor=ChartData.borderColor.value,
            lineColor=ChartData.lineColor_spline.value,
            xAxisTitle="",
            xAxisData=list(res_data["data"].keys()),
            yAxisTitle="NO OF QA",
            yAxisData=list(res_data["data"].values()),
            dataLabels_enabled="true",
            dataLabels_format=ChartData.dataLabels_format_1f.value,
            dataLabels_Color="black",
            gridLineWidth=ChartData.gridLineWidth.value,
        ),
        getSplineChart2=await SplineChart(
            chartName="SplineChart2",
            title="NEW TESTS CONDUCTED",
            subtitle=f"{selected_option_project.replace('_', ' ') + ' / ' if selected_option_project != 'ALL' else ''}{int(selected_option_year)}",
            max_width=ChartData.max_width.value,
            min_width=ChartData.min_width.value,
            height="",
            background_color=ChartData.background_color.value,
            borderColor=ChartData.borderColor.value,
            lineColor=ChartData.spline_effort.value,
            xAxisTitle="",
            xAxisData=list(execution_data["data"].keys()),
            yAxisTitle="NO OF TESTS",
            yAxisData=list(execution_data["data"].values()),
            dataLabels_enabled="true",
            dataLabels_format=ChartData.dataLabels_format_0f.value,
            dataLabels_Color="black",
            gridLineWidth=ChartData.gridLineWidth.value,
        ),
        getPieChart2=await PieChart(
            chartName="pie3",
            title=f"COST SUMMARY ~ {period[0]} - {period[-1]}",
            subtitle=f"{selected_option_project.replace('_', ' ') + '' if selected_option_project != 'ALL' else ''}",
            max_width=ChartData.max_width.value,
            min_width=ChartData.min_width.value,
            height=ChartData.height.value,
            background_color=ChartData.background_color.value,
            borderColor=ChartData.borderColor.value,
            colorByPoint="true",
            dataLabels_enabled="true",
            dataLabels_format=ChartData.dataLabels_format_m0f.value,
            dataLabels_font_size="11px",
            series_name="Value",
            series_data=dep_cost_per_dict,
        ),
    )
