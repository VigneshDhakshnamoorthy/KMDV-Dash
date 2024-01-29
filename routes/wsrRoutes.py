import asyncio
from datetime import datetime as dat
import math
from flask import Blueprint, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required
from routes.enumLinks import ChartData, FileAssociate, getUserName
from routes.dashRoutes import month_today,year_list

from utils.dataUtil import (
    filter_full_data,
    filterDataSummary,
    getChartDataTotal,
    getMonth,
    getSheetNames,
    getYearList,
    load_data,
    load_tables,
    weekDays,
)
from asyncio import to_thread

from utils.zynaCharts import ColumnChart, SplineChart

WSRPage = Blueprint("WSRPage", __name__, template_folder="templates")

@WSRPage.route("/summary/<project_name>/<project_year>", methods=["GET", "POST"])
@login_required
async def summary(project_name,project_year):
    project_name = project_name.upper()
    project_year = int(project_year)
    project_year = year_list[0] if project_year not in year_list else project_year
    selected_option_year = project_year    
    project_list = await asyncio.to_thread(current_user.get_projects_list)
    if project_name in project_list:
        if project_name != "favicon.ico":
            if (
                not project_name in FileAssociate.keys()
            ):
                return render_template("accounts/404.html")

        selected_option_project = project_name.upper()
        session["selected_project"] = project_name.upper()
        
        if request.method == "GET":
            selected_option_year = selected_option_year
            session["selected_year"] = selected_option_year
            
        if request.method == "POST" and "selected_year" in request.form:
            selected_option_year = request.form.get("selected_year")
            session["selected_year"] = selected_option_year
            return redirect(url_for('WSRPage.summary', project_name=selected_option_project,project_year=selected_option_year))

        efforts_chart_data = await asyncio.to_thread(
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
        resource_chart_data = await asyncio.to_thread(
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
        efforts_chart_data = await efforts_chart_data
        resource_chart_data = await resource_chart_data
        options_project = [entry["name"] for entry in efforts_chart_data]
        if not project_name in options_project:
            return render_template("accounts/projectKickStart.html", template=project_name)

     

        filtered_data_efforts = await asyncio.to_thread(
            lambda: filterDataSummary(efforts_chart_data, selected_option_project)
        )

        filtered_resource_cost = await asyncio.to_thread(
            lambda: filterDataSummary(resource_chart_data, selected_option_project)
        )
        total_efforts = [
            value
            for value in list(filtered_data_efforts[0]["data"].values())
            if isinstance(value, (int, float)) and not math.isnan(value)
        ]
        total_cost = [
            value
            for value in list(filtered_resource_cost[0]["data"].values())
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
        total_cost = "{:0,.0f}".format(math.ceil(sum(total_cost)))
        if len(avg_team) > 0:
            avg_team = "{:0,.0f}".format(sum(avg_team) / len(avg_team))
        else:
            avg_team = 0

        options_week = (
            await to_thread(getSheetNames, FileAssociate.get_value(project_name))
            if project_name != "favicon.ico"
            else await to_thread(getSheetNames, FileAssociate.ONETRACKER.value)
        )
        
        automation_percentage = await asyncio.to_thread(
        lambda: filter_full_data(
            "dataSources/monthData/dashSummary.xlsx",
            "Automation Percentage",
            "Project",
            selected_option_project,
            selected_option_year
        )
    )
        
        options_week = await options_week
        filtered_dates = [date_str for date_str in options_week if str(selected_option_year) in date_str]
        monthDatasummary =""
        weekdays=""
        wsr_bool = False
        if not FileAssociate.get_value(project_name) is None:
            if filtered_dates:
                tables_fromsheet = await to_thread(
                    load_tables, FileAssociate.get_value(project_name), filtered_dates[0]
                )
                tables_fromsheet = await tables_fromsheet
                monthDatasummary=tables_fromsheet[6].to_html(
                    classes="table caption-top table-bordered table-hover", index=False
                )
                weekdays = weekDays(filtered_dates[0])
            wsr_bool = True

        return render_template(
            "pages/wsr_summary.html",
            dropdown_project=options_project,
            dropdown_year=year_list,
            selected_project=selected_option_project,
            selected_year=int(selected_option_year),
            userName=getUserName(current_user),
            total_efforts=total_efforts,
            total_cost=total_cost,
            avg_team=await automation_percentage,
            wsr_bool=wsr_bool,
            weekdays=weekdays,
            getColumnChart1=await ColumnChart(
                chartName="ColumnChart1",
                title="TOTAL BUGS",
                subtitle=f"Project : {selected_option_project}",
                max_width=ChartData.max_width.value,
                min_width=ChartData.min_width.value,
                height="",
                background_color=ChartData.background_color.value,
                borderColor=ChartData.borderColor.value,
                lineColor=ChartData.lineColor_column.value,
                colorByPoint="false",
                xAxisTitle="",
                xAxisData=list(filtered_data_efforts[0]["data"].keys()),
                yAxisTitle="Bug",
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
            getSplineChart1=await SplineChart(
                chartName="SplineChart1",
                title="TOTAL EXECUTION",
                subtitle=f"Project : {selected_option_project}",
                max_width=ChartData.max_width.value,
                min_width=ChartData.min_width.value,
                height="",
                background_color=ChartData.background_color.value,
                borderColor=ChartData.borderColor.value,
                lineColor=ChartData.lineColor_spline.value,
                xAxisTitle="",
                xAxisData=list(filtered_resource_cost[0]["data"].keys()),
                yAxisTitle="Team Utilization",
                yAxisData=list(filtered_resource_cost[0]["data"].values()),
                dataLabels_enabled="true",
                dataLabels_format=ChartData.dataLabels_format_0f.value,
                dataLabels_Color="black",
                gridLineWidth=ChartData.gridLineWidth.value,
            ),
            monthDatasummary=monthDatasummary,
        )
    else:
        if (
            not project_name in FileAssociate.keys()
            or FileAssociate.get_value(project_name) is None
        ):
            return render_template("accounts/404.html")
        else:
            return render_template("accounts/wsrAuth.html")


@WSRPage.route("/<project_name>/<project_year>", methods=["GET", "POST"])
@login_required
async def pages(project_name,project_year):
    project_name = project_name.upper()
    if current_user.is_authenticated:
        project_list = await asyncio.to_thread(current_user.get_projects_list)
        if project_name in project_list:
            if project_name != "favicon.ico":
                if (
                    not project_name in FileAssociate.keys()
                    or FileAssociate.get_value(project_name) is None
                ):
                    return render_template("accounts/404.html")

            options_week = (
                await to_thread(getSheetNames, FileAssociate.get_value(project_name))
                if project_name != "favicon.ico"
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
                    load_tables, FileAssociate.get_value(project_name), selected_option
                )
                if project_name != "favicon.ico"
                else await to_thread(
                    load_tables, FileAssociate.ONETRACKER.value, selected_option
                )
            )
            tables_fromsheet = await tables_fromsheet
            return render_template(
                "pages/wsr.html",
                dropdown_week=options_week,
                selected_project=project_name,
                selected_dropdown=selected_option,
                selected_year = project_year,
                weekdays=weekDays(selected_option),
                userName=getUserName(current_user),
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
                weekDatasummary=tables_fromsheet[5].to_html(
                    classes="table caption-top table-bordered table-hover", index=False
                ),
                monthDatasummary=tables_fromsheet[6].to_html(
                    classes="table caption-top table-bordered table-hover", index=False
                ),
            )
        else:
            return render_template("accounts/wsrAuth.html")
