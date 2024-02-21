import math
from flask import (
    Blueprint,
    jsonify,
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
    filterDataSummary,
    getChartDataTotal,
    getDateNow,
    getMonth,
    getRowResource,
    getYearList,
    load_data,
    load_data_month_skip,
    sum_columns,
    sum_columns_row,
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


month_today = 2
year_list = getYearList(month=month_today)

DashboardPage = Blueprint("DashboardPage", __name__, template_folder="templates")


@DashboardPage.route("/dashboard", methods=["GET", "POST"])
@login_required
async def Dashboard():
    summary_efforts_fromsheet = await asyncio.to_thread(
        lambda: load_data(
            "dataSources/monthData/dashSummary.xlsx",
            "Efforts",
            0,
            getMonth(month=month_today),
        )
    )

    summary_cost_fromsheet = await asyncio.to_thread(
        lambda: load_data(
            "dataSources/monthData/dashSummary.xlsx",
            "Cost",
            0,
            getMonth(month=month_today),
        )
    )

    summary_resource_fromsheet = await asyncio.to_thread(
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
        filtered_years = await asyncio.to_thread(
            filter_active_years,
            project_name,
            year_list,
            "dataSources/monthData/dashSummary.xlsx",
            sheet_name="ActiveHistory",
        )
        filtered_years = await filtered_years

    print(filtered_years)
    project_year = filtered_years[0] if project_year not in filtered_years else project_year
    selected_option_year = project_year
    project_list = await asyncio.to_thread(current_user.get_projects_list)

    project_list = await asyncio.to_thread(
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

    efforts_chart_data = await asyncio.to_thread(
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
    cost_chart_data = await asyncio.to_thread(
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
    resource_chart_data = await asyncio.to_thread(
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

    filtered_data_efforts = await asyncio.to_thread(
        lambda: filterDataSummary(efforts_chart_data, selected_option_project)
    )

    eff_data = add_missing_dates_project(filtered_data_efforts[0])

    filtered_data_cost = await asyncio.to_thread(
        lambda: filterDataSummary(cost_chart_data, selected_option_project)
    )
    cost_data = add_missing_dates_project(filtered_data_cost[0])

    filtered_resource_cost = await asyncio.to_thread(
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

    wsr_bool = (not FileAssociate.get_value(session["selected_project"]) is None) and (int(selected_option_year) > 2022)
    
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

    summary_efforts_fromsheet = await asyncio.to_thread(
        lambda: load_data_month_skip(
            "dataSources/monthData/dashSummary.xlsx",
            "Efforts",
            0,
            getMonth(int(selected_option_year), month=month_today, max=max(year_list)),
            int(selected_option_year),
        )
    )

    summary_cost_fromsheet = await asyncio.to_thread(
        lambda: load_data_month_skip(
            "dataSources/monthData/dashSummary.xlsx",
            "Cost",
            0,
            getMonth(int(selected_option_year), month=month_today, max=max(year_list)),
            int(selected_option_year),
        )
    )

    summary_department_fromsheet = await asyncio.to_thread(
        lambda: load_data_month_skip(
            "dataSources/monthData/dashSummary.xlsx",
            "Department",
            0,
            getMonth(int(selected_option_year), month=month_today, max=max(year_list)),
            int(selected_option_year),
        )
    )

    summary_resource_fromsheet = await asyncio.to_thread(
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
    cost_dict = filter_data_by_rows(summary_cost_fromsheet, 1, -5).to_dict()
    dep_cost_dict = filter_data_by_rows(summary_cost_fromsheet, -7, "").to_dict()

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

    cost_per_dict = await asyncio.to_thread(
        lambda: sum_columns_row(cost_dict, selected_option_month)
    )

    cost_dep_client_marketing = await asyncio.to_thread(
        lambda: sum_columns(
            department_dfs["CLIENTS & MARKETING"], selected_option_month
        )
    )

    cost_dep_data_architecture = await asyncio.to_thread(
        lambda: sum_columns(
            department_dfs["DATA & ARCHITECTURE"], selected_option_month
        )
    )
    cost_dep_finance = await asyncio.to_thread(
        lambda: sum_columns(department_dfs["FINANCE"], selected_option_month)
    )
    cost_dep_investment = await asyncio.to_thread(
        lambda: sum_columns(department_dfs["INVESTMENT"], selected_option_month)
    )
    cost_dep_business_operation = await asyncio.to_thread(
        lambda: sum_columns(
            department_dfs["IT BUSINESS OPERATIONS"], selected_option_month
        )
    )

    dep_cost_per_dict = await asyncio.to_thread(
        lambda: sum_columns_row(dep_cost_dict, selected_option_month)
    )

    cost_list_dict = await asyncio.to_thread(
        lambda: getRowResource(
            summary_cost_fromsheet,
            ["Total T&M", "Projected Monthly Cost"],
            selected_option_month,
        )
    )
    cost_data = add_missing_dates(cost_list_dict)

    resource_list_dict = await asyncio.to_thread(
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
