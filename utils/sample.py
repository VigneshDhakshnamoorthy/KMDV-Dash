import sys
import pandas as pd
from datetime import datetime as dat

sys.path.append(".")
from utils.dataUtil import load_data

def sum_columns(df, month):
    month_index = df.columns.get_loc(month)
    df['Total'] = df.iloc[:, 1:month_index + 1].sum(axis=1)    
    return df[['Project', 'Total']]

projects_to_extract = ['Non Utilization', 'QA Summary']
df = load_data(
        "dataSources\\monthData\\dashSummary.xlsx", "Resource", 0, dat.now().month
    )


result = {}
for project in projects_to_extract:
    values = df.loc[df['Project'] == project, df.columns[1:]].values.flatten().tolist()
    result[project] = values
    
print("Result:", result['Non Utilization'])
print("Result:", result['QA Summary'])
