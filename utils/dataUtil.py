from datetime import datetime, timedelta
import openpyxl
import pandas as pd
from datetime import datetime as dat
from asyncio import to_thread



def getSheetNames(excel_file_path):
    try:
        with pd.ExcelFile(excel_file_path) as xls:
            sheet_names = xls.sheet_names
            sheet_names.reverse()
        return sheet_names
    except Exception as e:
        print(f"Error loading Excel file '{excel_file_path}': {str(e)}")
        return []
    
def weekDays(week):
    date_obj = datetime.strptime(week, "%d %b %Y")
    new_date_obj = date_obj + timedelta(days=4)
    formatted_date = date_obj.strftime("%d %b %Y")
    formatted_new_date = new_date_obj.strftime("%d %b %Y")
    return f"{formatted_date} - {formatted_new_date}"


def getTypeCount(df, typeName):
    return int(df.loc[df["Type"] == typeName, "Count"].values[0])


async def getSheetNames(excel_file_path):
    try:
        with pd.ExcelFile(excel_file_path) as xls:
            sheet_names = xls.sheet_names
            sheet_names.reverse()
        return sheet_names
    except Exception as e:
        print(f"Error loading Excel file '{excel_file_path}': {str(e)}")
        return []

load_data_dfs ={}

def get_or_append(key, new_value):
    if key in load_data_dfs:
        return load_data_dfs[key]
    else:
        load_data_dfs[key] = new_value
        return new_value
    
async def load_data(excel_file_path, sheet_name, start, end):
    df = await to_thread(pd.read_excel, excel_file_path, sheet_name, usecols=range(start, end))
    df = df.dropna(how="all")
    return get_or_append(f"{excel_file_path}_{sheet_name}_{start}_{end}", df)


def load_tables(excel_file_path, sheet_name):
    utilization_task_wise = load_data(excel_file_path, sheet_name, 0, 2)
    utilization_task_wise = utilization_task_wise.astype({"Hours.": "int"})

    utilization_resource_wise = load_data(excel_file_path, sheet_name, 3, 5)
    utilization_resource_wise = utilization_resource_wise.astype({"Hours..": "int"})
    task_last_week = load_data(excel_file_path, sheet_name, 6, 10)
    # task_last_week['ETC.'] = task_last_week['ETC.'].dt.strftime('%d-%b-%Y')
    task_next_week = load_data(excel_file_path, sheet_name, 11, 15)
    # task_next_week['ETC..'] = task_next_week['ETC..'].dt.strftime('%d-%b-%Y')
    defect = load_data(excel_file_path, sheet_name, 16, 23)
    # defect['ETC'] = defect['ETC'].dt.strftime('%d-%b-%Y')
    summary = load_data(excel_file_path, sheet_name, 24, 26)
    summary = summary.astype({"Count": "int"})

    weekDatasummary = load_data(excel_file_path, sheet_name, 27, 29)
    weekDatasummary = weekDatasummary.astype({"Week Count": "int"})

    monthDatasummary = load_data(excel_file_path, sheet_name, 30, 32)
    monthDatasummary = monthDatasummary.astype({"Total Count": "int"})

    dfs = [
        utilization_task_wise,
        utilization_resource_wise,
        task_last_week,
        task_next_week,
        defect,
        summary,
        weekDatasummary,
        monthDatasummary,
    ]
    for df in dfs:
        df.fillna("", inplace=True)
    return dfs

def getChartData(filePath, sheetName, set_index):
    summary_fromsheet = load_data(filePath, sheetName, 0, dat.now().month)
    decimal_places = 2
    summary_fromsheet = summary_fromsheet.round(decimal_places)
    summary_fromsheet = summary_fromsheet.set_index(set_index)
    summary_dict = summary_fromsheet.transpose().to_dict()
    chart_data = []
    for month, values in summary_dict.items():
        month_data = {"name": month, "data": values}
        chart_data.append(month_data)

    return chart_data


def filterDataSummary(chart_data, selected_option_project):
    filtered_data_efforts = [
        entry for entry in chart_data if entry["name"] == selected_option_project
    ]
    return filtered_data_efforts


def month_index_no(dictf, month):
    return dictf.columns.get_loc(month)


def sum_columns_resource(dictf, month):
    df = pd.DataFrame(dictf)
    df = df.iloc[1:-2, :]
    month_index = month_index_no(df, month)
    df["Total"] = df.iloc[:, 1 : month_index + 1].sum(axis=1)
    return df[["Project", "Total"]]


def sum_columns_cost(dictf, month):
    df = pd.DataFrame(dictf)
    df = df.iloc[1:-2, :]
    month_index = month_index_no(df, month)
    df["Total"] = df.iloc[:, 1 : month_index + 1].sum(axis=1)
    return df[["Project", "Total"]]


def sum_columns(dictf, month):
    df = pd.DataFrame(dictf)
    month_index = month_index_no(df, month)
    df["Total"] = df.iloc[:, 1 : month_index + 1].sum(axis=1)
    return df[["Project", "Total"]]


def getRowResource(dictf, projects_to_extract, month):
    month_index = month_index_no(dictf, month) + 1
    result = {}
    for project in projects_to_extract:
        values = (
            dictf.loc[dictf["Project"] == project, dictf.columns[1:month_index]]
            .values.flatten()
            .tolist()
        )
        columns = dictf.columns[1:month_index].tolist()
        result[project] = {"keys": columns, "values": values}
    return result

def getMonth():
    #month = dat.now().month
    month = 12
    return month
