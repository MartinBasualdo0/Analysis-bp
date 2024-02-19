import pandas as pd
import os
import json
from typing import Literal
from src.wrangling import _modify_bdp_code_d_c, _modify_bdp_code_anaf_enep



def clean_data_frame(df:pd.DataFrame):
    
    df = df.rename({df.columns[2]: "Descripción", df.columns[0]: "SDMX", df.columns[1]:"Codigo BDP"}, axis=1)
    df = _modify_bdp_code_anaf_enep(df)
    df['Codigo BDP'] = df.apply(_modify_bdp_code_d_c, axis=1)
    
    last_category = None
    for index, row in df.iterrows():
        if row['Descripción'] == 'Crédito' or row['Descripción'] == 'Débito':
            if last_category:
                if row['Descripción'] == 'Débito':
                    df.at[index, 'Descripción'] = last_category + ' Débito'
                else:
                    df.at[index, 'Descripción'] = last_category + ' Crédito'
        else:
            last_category = row['Descripción']

    # Drop rows and columns with too many NaN values
    df = df.dropna(axis=0, thresh=2).dropna(axis=1, thresh=2)

    return df

def _create_sdmx_description_dict(df, key_column:str, value_column:str):
    sdmx_description_dict = {}
    # Populate the dictionary
    for index, row in df.iterrows():
        # sdmx_description_dict[row['SDMX']] = row['Descripción']
        sdmx_description_dict[row[key_column]] = row[value_column]
    return sdmx_description_dict

def export_dictionary_to_json(dictionary, filename):
    # Ensure the data folder exists
    if not os.path.exists("data"):
        os.makedirs("data")
    filepath = os.path.join("data", filename)
    with open(filepath, 'w') as f:
        json.dump(dictionary, f, indent=4)

def main_write_dict(link_xls:list[str], key_column:Literal["Codigo BDP", "Descripción", "SDMX"], value_column:Literal["Codigo BDP", "Descripción", "SDMX"]):
    df = pd.read_excel(link_xls, sheet_name="Cuadro 14", header=5, skipfooter=6)
    cleaned_df = clean_data_frame(df)
    sdmx_description_dict = _create_sdmx_description_dict(cleaned_df, key_column, value_column)
    export_dictionary_to_json(sdmx_description_dict, f"{key_column}_{value_column}_dict.json")
    
    return sdmx_description_dict
