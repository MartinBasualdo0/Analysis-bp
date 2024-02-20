import pandas as pd
import numpy as np

def _modify_bdp_code_asset_liability(df:pd.DataFrame):
    def _assign_asset_liability(description):
        if description == 'Activos':
            return 'activo'
        elif description == 'Pasivos':
            return 'pasivo'
        else:
            return np.nan

    def _modify_bdp_code(description, bdp_code):
        if description == 'Activos':
            return 'A'
        elif description == 'Pasivos':
            return 'P'
        else:
            return bdp_code

    def _find_first_asset_or_liability(row, df):
        index_current = row.name
        while index_current >= 0:
            if 'activo_pasivo' in df.columns:
                value_previous = df.loc[index_current, 'activo_pasivo']
                if pd.notnull(value_previous):
                    return value_previous
            index_current -= 1
        return np.nan

    def modify_bdp_code_with_asset_liability(asset_liability, first_asset_or_liability, bdp_code):
        if pd.isna(asset_liability):
            if first_asset_or_liability == 'activo':
                return 'A.' + str(bdp_code)
            elif first_asset_or_liability == 'pasivo':
                return 'P.' + str(bdp_code)
        return bdp_code

    # Aplicamos las funciones para modificar 'Codigo BDP' y añadir 'activo_pasivo'
    df['Codigo BDP'] = df.apply(lambda x: _modify_bdp_code(x['Descripción'], x['Codigo BDP']), axis=1)
    df['activo_pasivo'] = df['Descripción'].apply(_assign_asset_liability)

    # Encontramos el primer activo o pasivo y lo aplicamos para modificar 'Codigo BDP'
    df['first_a_o_p'] = df.apply(lambda x: _find_first_asset_or_liability(x, df), axis=1)
    df['Codigo BDP'] = df.apply(lambda x: modify_bdp_code_with_asset_liability(x['activo_pasivo'], x['first_a_o_p'], x['Codigo BDP']), axis=1)

    df = df.drop(["activo_pasivo","first_a_o_p"], axis=1)
    return df

def pii_first_clean_step_for_dict(xls:str):
    df = pd.read_excel(xls, sheet_name = "Cuadro 22", header=4, skipfooter=6)
    df = df.rename({df.columns[1]:"Codigo BDP", df.columns[2]: "Descripción", df.columns[0]:"SDMX"}, axis = 1)
    df = df.drop(df.columns[3:13], axis=1) #Hay años sin trimestres
    df = _modify_bdp_code_asset_liability(df)
    return df

def clean_pii_data_frame(xls:str):
    df = pii_first_clean_step_for_dict(xls)
    df = (
        df.filter(regex='^(?!Total).*')
        .iloc[1:]
        .drop(["SDMX", "Descripción"], axis=1)
        .dropna(axis=0, thresh=2)
        .dropna(axis=1, thresh=2)
        .reset_index(drop=True)
    )

    df.set_index("Codigo BDP", inplace=True)
    df = df.T
    df.index = pd.date_range(start="2016-01-01", periods=len(df),freq='QE')
    return df