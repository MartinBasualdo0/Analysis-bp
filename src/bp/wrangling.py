import numpy as np
import pandas as pd

def _modify_bdp_code_d_c(row):
    codigo = row['Codigo BDP']
    descripcion = row['Descripción']
    
    if descripcion == 'Crédito':
        return codigo + '.X'
    elif descripcion == 'Débito':
        return codigo + '.Y'
    else:
        return codigo
    

descriptions_mapping = {
    'Adquisición neta de activos financieros': 'ANAF',
    'Emisión neta de pasivos': 'ENP'
}

def _modify_bdp_code_anaf_enep(df:pd.DataFrame):
    def assign_description_value(row):
        return descriptions_mapping.get(row['Descripción'], np.nan)

    df['anaf_enp'] = df.apply(assign_description_value, axis=1)

    df['n_jerarquía'] = df['Codigo BDP'].str.count('\.') +  1

    df['cod_anaf_mas_cercano'] = df['Codigo BDP'].where(df['anaf_enp'] == 'ANAF').ffill().fillna(np.nan)
    df['n_jerarquía_anaf_mas_cercano'] = df['n_jerarquía'].where(df['anaf_enp'] == 'ANAF').ffill().fillna(np.nan)

    def calculate_dependency(row):
        return (pd.notnull(row['n_jerarquía_anaf_mas_cercano']) and
                row['n_jerarquía'] > row['n_jerarquía_anaf_mas_cercano'] and
                row['Codigo BDP'].startswith(row['cod_anaf_mas_cercano']))

    df['depende_anaf_enp'] = df.apply(calculate_dependency, axis=1)

    def calculate_own_code(row):
        if pd.isnull(row['cod_anaf_mas_cercano']):
            return np.nan
        codigo_bdp = str(row['Codigo BDP'])  # Convert to string
        index_anaf = codigo_bdp.find(row['cod_anaf_mas_cercano'])
        if index_anaf != -1:
            return codigo_bdp[index_anaf + len(row['cod_anaf_mas_cercano']):]
        return np.nan
    df['codigo_propio'] = df.apply(calculate_own_code, axis=1)

    def find_first_anaf_or_enp(row):
        index_current = row.name
        while index_current >=  0:
            value_previous = df.at[index_current, 'anaf_enp']
            if pd.notnull(value_previous):
                return value_previous
            index_current -=  1
        return np.nan
    df['primero_anaf_o_enp'] = df.apply(find_first_anaf_or_enp, axis=1)

    def create_new_code(row):
        if row['depende_anaf_enp']:
            return f"{row['cod_anaf_mas_cercano']}.{row['primero_anaf_o_enp']}{row['codigo_propio']}"
        elif pd.notnull(row['anaf_enp']):
            return f"{row['Codigo BDP']}.{row['anaf_enp']}"
        else:
            return row['Codigo BDP']
    df['Codigo BDP'] = df.apply(create_new_code, axis=1)
    df = df.drop(["codigo_propio", "primero_anaf_o_enp", "depende_anaf_enp",
                  "n_jerarquía_anaf_mas_cercano", "cod_anaf_mas_cercano", "n_jerarquía",
                  "anaf_enp"], axis=1)
    return df


def _handle_last_category(df: pd.DataFrame):
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
    
    return df

def bp_first_clean_step_for_dict(xls:str):
    df = pd.read_excel(xls, sheet_name = "Cuadro 14", header=4, skipfooter=6)
    df= df.rename({df.columns[1]:"Codigo BDP", df.columns[2]: "Descripción", df.columns[0]:"SDMX"}, axis = 1)
    df.loc[df['SDMX'] == "Q.N.AR.W1.S121.S1.T.A.FA.P.F5._Z.USD._T.M.N", 'Codigo BDP'] = "3.2.1.1"
    df.loc[df['SDMX'] == "Q.N.AR.W1.S121.S1.T.L.FA.P.F5._Z.USD._T.M.N", 'Codigo BDP'] = "3.2.1.1"
    df = _modify_bdp_code_anaf_enep(df)
    df['Codigo BDP'] = df.apply(_modify_bdp_code_d_c, axis=1)
    df = _handle_last_category(df)
    return df

def clean_bp_data_frame(xls:str):
    df = bp_first_clean_step_for_dict(xls)
    df = (
        df.filter(regex='^(?!Total).*')
        .iloc[1:]
        .drop(["SDMX", "Descripción"], axis=1)
        .dropna(axis=0, thresh=2)
        .dropna(axis=1, thresh=2)
    )

    df.set_index("Codigo BDP", inplace=True)
    df = df.T
    df.index = pd.date_range(start="2006-01-01", periods=len(df),freq='QE')
    return df
