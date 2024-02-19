import pandas as pd
import asyncio
import sys
sys.path.append(".")
from routes.dashRoutes import year_list

def load_full_data(excel_file_path, sheet_name):
    return pd.read_excel(excel_file_path, sheet_name)

def filter_active_years(project_name, year_list, excel_file_path, sheet_name):
    df = load_full_data(excel_file_path, sheet_name)
    active_years = []
    if project_name in df['Project'].values:
        project_data = df[df['Project'] == project_name]
        for year in year_list:
            if str(year) in project_data.columns:
                if project_data[str(year)].values[0] == 'Active':
                    active_years.append(year)
    return active_years

# Example usage
project_name = 'SMA'
excel_file_path = 'dataSources/monthData/dashSummary.xlsx'
sheet_name = 'ActiveHistory'

filtered_years = filter_active_years(project_name, year_list, excel_file_path, sheet_name)
print("Filtered active years for project {}: {}".format(project_name, filtered_years))


