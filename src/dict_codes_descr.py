import pandas as pd
import os
import json
from typing import Literal
from src.bp.wrangling import bp_first_clean_step_for_dict
from src.pii.wrangling import pii_first_clean_step_for_dict


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

def main_write_dict(link_xls:list[str], 
                    report:Literal["bp", "pii", "de"], #falta desarrollar "de"
                    key_column:Literal["Codigo BDP", "Descripción", "SDMX"], 
                    value_column:Literal["Codigo BDP", "Descripción", "SDMX"],
                    ):
    if report == "bp":
        df = bp_first_clean_step_for_dict(link_xls)
    elif report == "pii":
        df = pii_first_clean_step_for_dict(link_xls)
    df = df.dropna(axis=0, thresh=2).dropna(axis=1, thresh=2)
    sdmx_description_dict = _create_sdmx_description_dict(df, key_column, value_column)
    export_dictionary_to_json(sdmx_description_dict, f"{report}_{key_column}_{value_column}_dict.json")
    
    return sdmx_description_dict
