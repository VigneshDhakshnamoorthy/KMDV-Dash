import copy
from datetime import datetime, timedelta
from typing import Coroutine, Hashable
import pandas as pd
from pandas import DataFrame
from datetime import datetime as dat
from asyncio import to_thread
from _collections_abc import dict_values

load_data_dfs:dict = {}

pd.set_option("display.float_format", lambda x: "{:.0f}".format(x))
start_year = 2021
report_start_year = 2021


def getSheetNames(excel_file_path) -> list[int | str] | list:
    key:str = f"sheet_names_{excel_file_path}"

    if key in load_data_dfs:
        return load_data_dfs[key]

    try:
        with pd.ExcelFile(excel_file_path) as xls:
            sheet_names:list[int | str] = xls.sheet_names
            sheet_names.reverse()
        load_data_dfs[key] = sheet_names
        return sheet_names
    except Exception as e:
        print(f"Error loading Excel file '{excel_file_path}': {str(e)}")
        return []


def weekDays(week) -> str:
    date_obj: datetime = datetime.strptime(week, "%d %b %Y")
    new_date_obj: datetime = date_obj + timedelta(days=4)
    formatted_date: str = date_obj.strftime("%d %b %Y")
    formatted_new_date: str = new_date_obj.strftime("%d %b %Y")
    return f"{formatted_date} - {formatted_new_date}"


def getTypeCount(df, typeName) -> int:
    return int(df.loc[df["Type"] == typeName, "Count"].values[0])


async def getSheetNames(excel_file_path) -> list[int | str] | list:
    try:
        with pd.ExcelFile(excel_file_path) as xls:
            sheet_names: list[int | str] = xls.sheet_names
            sheet_names.reverse()
        return sheet_names
    except Exception as e:
        print(f"Error loading Excel file '{excel_file_path}': {str(e)}")
        return []


@staticmethod
def getDateNow() -> datetime:
    return dat.now()


@staticmethod
def getYear() -> int:
    return getDateNow().year


def getMonth(year_selection=getYear(), month=getDateNow().month, max=getYear()) -> int:
    dif: int = year_selection - report_start_year
    if (
        dif == 0
        or max > report_start_year
        and (max > year_selection or month % 12 == 1)
    ):
        month = 13
    return (dif * 12) + month


async def load_data(excel_file_path, sheet_name, start, end) -> DataFrame:
    key: str = f"{excel_file_path}_{sheet_name}_{start}_{end}"
    if key in load_data_dfs:
        return load_data_dfs[key]
    try:
        df = await to_thread(
            pd.read_excel, excel_file_path, sheet_name, usecols=range(start, end)
        )
    except pd.errors.ParserError:
        df = await to_thread(pd.read_excel, excel_file_path, sheet_name)

    df = df.dropna(how="all")

    load_data_dfs[key] = df
    return df


async def load_full_data(excel_file_path, sheet_name) -> DataFrame:
    return pd.read_excel(excel_file_path, sheet_name)


async def filter_active_projects(project_list, year, excel_file_path, sheet_name) -> list:
    df: DataFrame = await load_full_data(excel_file_path, sheet_name)
    active_projects:list = []
    for project in project_list:
        project_status = df.loc[df["Project"] == project, str(year)].values
        if len(project_status) > 0 and project_status[0] == "Active":
            active_projects.append(project)
    return active_projects


async def filter_active_years(project_name, year_list, excel_file_path, sheet_name) -> list:
    df: DataFrame = await load_full_data(excel_file_path, sheet_name)
    active_years:list = []
    if project_name in df["Project"].values:
        project_data = df[df["Project"] == project_name]
        for year in year_list:
            if str(year) in project_data.columns:
                if project_data[str(year)].values[0] == "Active":
                    active_years.append(year)
    return active_years


async def filter_active_projects_df(df, year, excel_file_path, sheet_name) -> DataFrame:
    project_list = df["Project"].tolist()
    active_projects:list = await filter_active_projects(
        project_list, year, excel_file_path, sheet_name
    )
    filtered_df = df[df["Project"].isin(active_projects)]
    return filtered_df


async def filter_full_data(
    excel_file_path, sheet_name, column_name, project_name, year
) -> DataFrame | None:
    df: DataFrame = await load_full_data(excel_file_path=excel_file_path, sheet_name=sheet_name)
    filtered_data:DataFrame = df[(df[column_name] == project_name) & (df[str(object=year)].notna())]
    if not filtered_data.empty:
        return filtered_data.iloc[0][str(object=year)]
    else:
        return None


async def load_data_month_skip(
    excel_file_path, sheet_name, start, end, year_selection=dat.now().year
) -> DataFrame:
    key: str = f"{excel_file_path}_{sheet_name}_{start}_{end}_{year_selection}"
    if key in load_data_dfs:
        return load_data_dfs[key]

    skip_columns = []
    total_columns = await to_thread(pd.read_excel, excel_file_path, sheet_name, nrows=0)
    total_columns = total_columns.shape[1]
    end = min(end, total_columns)
    if not end % 12 == 1:
        skip_columns: list[int] = [i for i in range(1, ((end // 12) * 12) + 1)]
    else:
        skip_columns = [i for i in range(1, (abs((end // 12) - 1) * 12) + 1)]

    columns_to_read: list[int] = [col for col in range(start, end) if col not in skip_columns]

    # total_columns = pd.read_excel(excel_file_path, sheet_name, nrows=0).shape[1]

    # columns_to_read = [col for col in range(start, end) if col < total_columns and col not in skip_columns]

    try:
        df = await to_thread(
            pd.read_excel, excel_file_path, sheet_name, usecols=columns_to_read
        )
    except pd.errors.ParserError:
        df = await to_thread(pd.read_excel, excel_file_path, sheet_name)

    df:DataFrame = df.dropna(how="all")
    load_data_dfs[key] = df
    return df


async def load_data_specific(
    excel_file_path, sheet_name, col_start, col_end, row_start, row_end
) -> DataFrame:
    key: str = f"{excel_file_path}_{sheet_name}_{col_start}_{col_end}_{row_start}_{row_end}"
    if key in load_data_dfs:
        return load_data_dfs[key]

    df = await to_thread(
        pd.read_excel,
        excel_file_path,
        sheet_name,
        usecols=range(col_start, col_end),
        skiprows=range(1, row_start),
    )
    df = df.head(row_end - row_start)
    df = df.dropna(how="all")

    load_data_dfs[key] = df
    return df


def filter_data_by_rows(df, start_row, end_row) -> DataFrame:
    if not end_row == "":
        filtered_df = df.iloc[start_row - 1 : end_row]
    else:
        filtered_df = df.iloc[start_row - 1 :]
    return filtered_df


async def removeDot(df) -> DataFrame:
    mod_df:DataFrame = df.copy()
    mod_df.rename(columns=lambda x: x.replace(".", ""), inplace=True)
    return mod_df


async def load_tables(excel_file_path, sheet_name) -> list[DataFrame]:
    utilization_task_wise: DataFrame = await load_data(excel_file_path, sheet_name, 0, 2)
    # utilization_task_wise = utilization_task_wise.astype({"Hours.": "int"})
    utilization_task_wise = await removeDot(utilization_task_wise)

    utilization_resource_wise: DataFrame = await load_data(excel_file_path, sheet_name, 3, 5)
    # utilization_resource_wise = utilization_resource_wise.astype({"Hours..": "int"})
    utilization_resource_wise = await removeDot(utilization_resource_wise)

    task_last_week: DataFrame = await load_data(excel_file_path, sheet_name, 6, 10)
    # task_last_week['ETC.'] = task_last_week['ETC.'].dt.strftime('%d-%b-%Y')
    task_last_week = await removeDot(task_last_week)

    task_next_week: DataFrame = await load_data(excel_file_path, sheet_name, 11, 15)
    # task_next_week['ETC..'] = task_next_week['ETC..'].dt.strftime('%d-%b-%Y')
    task_next_week = await removeDot(task_next_week)

    defect: DataFrame = await load_data(excel_file_path, sheet_name, 16, 23)
    # defect['ETC'] = defect['ETC'].dt.strftime('%d-%b-%Y')
    defect = await removeDot(defect)

    week_table_header:str = 'Activity This Week'
    month_table_header:str = 'Project Metrics Since Inception'

    weekDatasummary: DataFrame = await load_data(excel_file_path, sheet_name, 24, 26)
    weekDatasummary = await removeDot(weekDatasummary)
    # weekDatasummary = weekDatasummary.astype({"Week Count": "int"})
    replace_weekDatasummary_dict: dict[str, str] = {
    'Manual test cases created': 'New Scripts Created',
    'Automation test cases created': 'New Scripts Automated'
    }
    # weekDatasummary[week_table_header] = weekDatasummary[week_table_header].replace(replace_weekDatasummary_dict)

    monthDatasummary: DataFrame = await load_data(excel_file_path, sheet_name, 27, 29)
    monthDatasummary = await removeDot(monthDatasummary)
    # monthDatasummary = monthDatasummary.astype({"Total Count": "int"})
    replace_monthDatasummary_dict: dict[str, str] = {
        'Manual test cases created': 'Total Scripts',
        'Automation test cases created': 'Total Scripts Automated',
        'Bugs identified':'Total Bugs'
        }
    # monthDatasummary[month_table_header] = monthDatasummary[month_table_header].replace(replace_monthDatasummary_dict)
    # monthDatasummary.loc[monthDatasummary[month_table_header] == 'Automation coverage', 'Count'] = (monthDatasummary['Count'] * 100).astype(int).astype(str) + '%'

    dfs: list[DataFrame] = [
        utilization_task_wise,
        utilization_resource_wise,
        task_last_week,
        task_next_week,
        defect,
        weekDatasummary,
        monthDatasummary,
    ]
    for df in dfs:
        df.fillna("", inplace=True)
    return dfs


async def getChartData(filePath, sheetName, set_index) -> list:
    summary_fromsheet = await load_data(filePath, sheetName, 0, getMonth())
    decimal_places = 2
    summary_fromsheet: DataFrame = summary_fromsheet.round(decimal_places)
    summary_fromsheet = summary_fromsheet.set_index(set_index)
    summary_dict: dict[Hashable, Any] = summary_fromsheet.transpose().to_dict()
    chart_data:list = []
    for month, values in summary_dict.items():
        month_data = {"name": month, "data": values}
        chart_data.append(month_data)

    return chart_data

async def getSinceData2(sheetName, end_month, project_name, project_list) -> list:
    efforts_since_fromsheet = await to_thread(
        load_data, "dataSources/monthData/dashSummary.xlsx", sheetName, 0, end_month
    )
    efforts_since_fromsheet: DataFrame = await efforts_since_fromsheet
    if project_name == "ALL":
        efforts_since_fromsheet = efforts_since_fromsheet[efforts_since_fromsheet['Project'].isin(project_list)]
    else:
        efforts_since_fromsheet = efforts_since_fromsheet[efforts_since_fromsheet['Project']== project_name]
    efforts_since_fromsheet = efforts_since_fromsheet.set_index('Project')
    efforts_since_fromsheet = efforts_since_fromsheet.transpose().to_dict()
    print(efforts_since_fromsheet)
    total_sum = 0
    list_since:list = []
    for month_values in efforts_since_fromsheet.values():
        month_since_list:list =[value for value in month_values.values() if not pd.isna(value)]
        if month_since_list:
            list_since.append(month_since_list)
        total_sum += sum(month_since_list)
    return list_since

async def getSinceData(sheetName, end_month, project_name, project_list) -> dict_values:
    efforts_since_fromsheet = await to_thread(
        load_data, "dataSources/monthData/dashSummary.xlsx", sheetName, 0, end_month
    )
    efforts_since_fromsheet: DataFrame = await efforts_since_fromsheet
    if project_name == "ALL":
        efforts_since_fromsheet = efforts_since_fromsheet[efforts_since_fromsheet['Project'].isin(project_list)]
    else:
        efforts_since_fromsheet = efforts_since_fromsheet[efforts_since_fromsheet['Project']== project_name]
    efforts_since_fromsheet = efforts_since_fromsheet.set_index('Project')
    efforts_since_fromsheet = efforts_since_fromsheet.transpose().to_dict()
    total_sum = 0
    list_since:list = []
    for month_values in efforts_since_fromsheet.values():
        month_since_list:list =[value for value in month_values.values() if not pd.isna(value)]
        if month_since_list:
            list_since.append(month_since_list)
        total_sum += sum(month_since_list)
        
    monthly_totals:dict = {}
    for project, values in efforts_since_fromsheet.items():
            for month, value in values.items():
                        if not pd.isna(value) and not isinstance(value, str) and not isinstance(value, bool):
                            if month not in monthly_totals:
                                monthly_totals[month] = 0
                            monthly_totals[month] += value

    return monthly_totals.values()

async def getSinceDataSum(sheetName, end_month, project_name, project_list) -> int:
    list_since:Coroutine[dict_values] = await to_thread(getSinceData,sheetName, end_month, project_name, project_list)
    list_since:dict_values = await list_since
    return sum(list_since)

async def getSinceDataAvg(sheetName, end_month, project_name, project_list) -> float:
    list_since:Coroutine[dict_values] = await to_thread(getSinceData,sheetName, end_month, project_name, project_list)
    list_since:dict_values = await list_since
    return 0 if len(list_since) == 0 else sum(list_since)/len(list_since)

async def getChartDataTotal(
    filePath,
    sheetName,
    set_index,
    start,
    end=None,
    projects_list=None,
    month=getMonth(),
    year_selection=dat.now().year,
    all_total = True,
) -> list[dict]:
    summary_fromsheet = await load_data_month_skip(
        filePath, sheetName, 0, month, year_selection
    )
    decimal_places = 2
    summary_fromsheet = summary_fromsheet.set_index(set_index)
    if end is None:
        end = len(summary_fromsheet) + 1
    summary_fromsheet = summary_fromsheet.iloc[start:end]
    summary_fromsheet = summary_fromsheet.loc[
        summary_fromsheet.index.isin(projects_list)
    ]
    if all_total:
        total_row = summary_fromsheet.sum(axis=0)
        total_row.name = "ALL"
        summary_fromsheet = summary_fromsheet._append(total_row)

    summary_fromsheet = summary_fromsheet.round(decimal_places)

    summary_dict = summary_fromsheet.transpose().to_dict()
    sorted_chart_data = sorted(summary_dict.items(), key=lambda x: x[0])

    if all_total:
        total_entry = next(
            entry for entry in sorted_chart_data if entry[0] == total_row.name
        )
        sorted_chart_data.remove(total_entry)
        sorted_chart_data.insert(0, total_entry)
    chart_data:list[dict] = [
        {"name": month, "data": values} for month, values in sorted_chart_data
    ]

    return chart_data


def filterDataSummary(chart_data, selected_option_project) -> list:
    filtered_data_efforts = [
        entry for entry in chart_data if entry["name"] == selected_option_project
    ]
    return filtered_data_efforts


def month_index_no(dictf, month) -> int:
    return dictf.columns.get_loc(month)


def sum_columns_row(dictf, month) -> DataFrame:
    df = pd.DataFrame(dictf)
    df:DataFrame = df.iloc[1:-2, :]
    month_index: int = month_index_no(df, month)
    df["Total"] = df.iloc[:, 1 : month_index + 1].sum(axis=1)
    return df[["Project", "Total"]]


def sum_columns(dictf, month) -> DataFrame:
    df = pd.DataFrame(dictf)
    month_index = month_index_no(df, month)
    df["Total"] = df.iloc[:, 1 : month_index + 1].sum(axis=1)
    filtered_df = df[df["Total"] > 0]
    return filtered_df[["Project", "Total"]]


def getRowResource(dictf, projects_to_extract, month) -> dict:
    month_index: int = month_index_no(dictf, month) + 1
    result:dict = {}
    for project in projects_to_extract:
        values = (
            dictf.loc[dictf["Project"] == project, dictf.columns[1:month_index]]
            .values.flatten()
            .tolist()
        )
        columns:list = dictf.columns[1:month_index].tolist()
        result[project] = {"keys": columns, "values": values}
    return result


def getYearList(year=getYear(), month=getDateNow().month) -> list[int]:
    if month > 1:
        yearList: list[int] = [i for i in range(start_year, year + 1)]
    else:
        yearList = [i for i in range(start_year, year)]
    return yearList[::-1]


def add_missing_dates(data):
    some_data = copy.deepcopy(data)

    def extract_year(date_str):
        return date_str.split()[1]

    def generate_missing_dates(year, keys) -> list[dict[str]]:
        months: list[str] = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        existing_months:list = [key.split()[0] for key in keys]
        missing_dates:list[str] = [
            f"{month} {year}" for month in months if month not in existing_months
        ]
        return [{"keys": [f"{month}"], "values": [0]} for month in missing_dates]

    for col, values in some_data.items():
        year = extract_year(values["keys"][0])
        missing_dates = generate_missing_dates(year, values["keys"])
        some_data[col]["keys"].extend([item["keys"][0] for item in missing_dates])
        some_data[col]["values"].extend([""] * len(missing_dates))

    return some_data


def add_missing_dates_project(data):
    some_data = copy.deepcopy(data)

    keys = list(some_data["data"].keys())

    year = keys[0].split()[1]

    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    expected_keys:list = []

    for month in months:
        key: str = f"{month} {year}"
        if key not in keys:
            expected_keys.append(key)

    for key in expected_keys:
        some_data["data"][key] = ""

    return some_data
