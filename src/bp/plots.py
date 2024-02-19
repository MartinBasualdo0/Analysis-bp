import pandas as pd
import plotly.graph_objects as go

def filter_code(df:pd.DataFrame, componente:str, desagregacion:bool = False):
    '''La desagregación no debería servir para la cuenta financiera'''
    filtered_columns = [col for col in df.columns if col.startswith(componente) and len(col.split(".")) <= (len(componente.split(".")) + 1)]
    df = df[filtered_columns]
    if not desagregacion:
        df = df.loc[:, ~df.columns.str.endswith(('X', 'Y'))]
    else:
        df = df[[*df.columns[df.columns.str.endswith(('X', 'Y'))].tolist(), componente]]
    return df

def plot_segun_codigo(df:pd.DataFrame, dict_bdpcode_description:dict ,componente:str, desagregacion:bool = False, anio_desde:int = 2006):
    df = filter_code(df, componente, desagregacion)
    df = df[str(anio_desde):]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x= df.index, y = df[componente], name = dict_bdpcode_description[componente], line_width = 4),)
    for columna in df.columns:
        if columna == componente:
            pass
        else:
            fig.add_trace(go.Bar(x = df.index, y = df[columna], name = dict_bdpcode_description[columna]))
            
    fig.update_layout(template = None, barmode = "relative", separators = ",.",
                    title_text = f"Evolución de {dict_bdpcode_description[componente]} y sus principales componentes<br><sup> En millones de dólares")
    fig.update_yaxes(tickformat = ",")
    return fig