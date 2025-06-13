import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import dash
from dash import html, dcc, dash_table, callback, Input, Output, State
import dash_bootstrap_components as dbc
from openpyxl import load_workbook
import os
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Modal de información
modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Cómo usar el Portal de Rentabilidades", 
                                   style={'fontFamily': 'SuraSans-SemiBold'})),
    dbc.ModalBody([
        html.P("Bienvenido al Portal de Rentabilidades de SURA Investments", 
               style={'fontFamily': 'SuraSans-SemiBold', 'fontSize': '18px'}),
        html.Hr(),
        html.H5("Navegación:", style={'fontFamily': 'SuraSans-SemiBold'}),
        html.Ul([
            html.Li("Rentabilidad Acumulada: Visualiza el crecimiento acumulado de los fondos", 
                    style={'fontFamily': 'SuraSans-Regular'}),
            html.Li("Rentabilidad Anualizada: Consulta el rendimiento anual promedio", 
                    style={'fontFamily': 'SuraSans-Regular'}),
            html.Li("Rentabilidad por Año: Compara el desempeño año a año", 
                    style={'fontFamily': 'SuraSans-Regular'})
        ]),
        html.Hr(),
        html.P("Los datos se actualizan diariamente con información de Bloomberg.", 
               style={'fontFamily': 'SuraSans-Regular', 'fontStyle': 'italic'}),
        html.Hr(),
        html.P("NOTA: Las selecciones de fondos se sincronizan automáticamente entre todas las pestañas.", 
               style={'fontFamily': 'SuraSans-SemiBold', 'color': '#0B2DCE'})
    ]),
    dbc.ModalFooter(
        dbc.Button("Cerrar", id="close-modal", className="ms-auto", 
                   style={'fontFamily': 'SuraSans-Regular'})
    ),
], id="info-modal", is_open=False, size="lg")

# Modal para gráfico en pantalla completa
modal_grafico = dbc.Modal([
    dbc.ModalHeader([
        dbc.ModalTitle("Retornos Acumulados - Vista Completa", 
                      style={'fontFamily': 'SuraSans-SemiBold'}),
    ], close_button=True),
    dbc.ModalBody([
        dcc.Graph(
            id='grafico-retornos-modal', 
            style={'height': '85vh', 'width': '100%'},
            config={
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToAdd': ['toImage'],
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': 'retornos_acumulados_fullscreen',
                    'height': 1200,
                    'width': 1800,
                    'scale': 2
                }
            }
        )
    ], style={'padding': '5px'}),
], id="modal-grafico", is_open=False, size="xl", centered=True, 
   style={'maxWidth': '100', 'maxHeight': '95vh'})

# Barra superior blanca
top_navbar = dbc.Navbar(
    dbc.Container([
        html.Img(
            src="/assets/sura_logo.png", 
            height="50px", 
            style={'marginRight': '20px'}
        ),
        html.Div([
            dbc.Button([
                html.I(className="fas fa-info-circle", style={'marginRight': '8px'}),
                "Información"
            ], 
            id="info-button", 
            color="light", 
            outline=True,
            style={
                'fontFamily': 'SuraSans-Regular',
                'color': '#333',
                'borderColor': '#333'
            })
        ], style={'marginLeft': 'auto'})
    ], fluid=True, style={'display': 'flex', 'alignItems': 'center'}),
    color="white",
    dark=False,
    sticky="top",
    style={'borderBottom': '1px solid #e0e0e0', 'height': '70px'}
)

# Barra inferior negra
bottom_navbar = html.Div([
   dbc.Container([
       html.H3(
           "INVESTMENTS", 
           style={
               'color': 'white', 
               'margin': '0', 
               'fontFamily': 'SuraSans-SemiBold',
               'fontSize': '24px',
               'letterSpacing': '2px'
           }
       )
   ], fluid=True, style={'display': 'flex', 'alignItems': 'center', 'height': '100%'})
], style={
   'backgroundColor': '#000000',
   'height': '50px',
   'width': '100%'
})

# Pestañas de navegación
tabs = dbc.Tabs([
   dbc.Tab(label="Rentabilidad Acumulada", tab_id="acumulada", 
           label_style={'fontFamily': 'SuraSans-Regular', 'fontWeight': 'bold'}),
   dbc.Tab(label="Rentabilidad Anualizada", tab_id="anualizada", 
           label_style={'fontFamily': 'SuraSans-Regular', 'fontWeight': 'bold'}),
   dbc.Tab(label="Rentabilidad por Año", tab_id="por_ano", 
           label_style={'fontFamily': 'SuraSans-Regular', 'fontWeight': 'bold'}),
], id="tabs", active_tab="acumulada", style={'marginTop': '20px'})

# CONTROLES CON SINCRONIZACIÓN
controles_acumulada = html.Div([
    html.H2("Rentabilidad Acumulada", 
            style={'fontFamily': 'SuraSans-SemiBold', 'marginBottom': '20px'}),
    
    dbc.Row([
        dbc.Col([
            html.Label("Moneda:", style={'fontFamily': 'SuraSans-SemiBold'}),
            dcc.Dropdown(
                id='moneda-selector-acumulada',
                options=[
                    {'label': 'Pesos Chilenos (CLP)', 'value': 'CLP'},
                    {'label': 'Dólares (USD)', 'value': 'USD'}
                ],
                value='CLP',
                style={'fontFamily': 'SuraSans-Regular'}
            )
        ], width=3),
        dbc.Col([
            html.Label("Filtrar Fondos:", 
                style={'fontFamily': 'SuraSans-SemiBold'}),
            dcc.Dropdown(
                id='fondos-selector-acumulada',
                options=[],
                value=[],
                multi=True,
                style={'fontFamily': 'SuraSans-Regular'}
            )
        ], width=9)
    ], style={'marginBottom': '30px'}),
    
    html.H5("Tabla de Rentabilidades:", style={'fontFamily': 'SuraSans-SemiBold', 'marginBottom': '15px'}),
    html.Div(id='tabla-rentabilidades-acumulada'),
    
    html.H5("Gráfico de Retornos Acumulados:", style={'fontFamily': 'SuraSans-SemiBold', 'marginTop': '40px', 'marginBottom': '15px'}),
    
    dbc.Row([
        dbc.Col([
            dbc.Button([
                html.I(className="fas fa-expand", style={'marginRight': '8px'}),
                "Ver en Pantalla Completa"
            ], 
            id="btn-pantalla-completa", 
            color="primary", 
            outline=True,
            size="sm",
            style={'fontFamily': 'SuraSans-Regular', 'marginBottom': '10px'})
        ], width=12, style={'textAlign': 'right'})
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Label("Desde:", style={'fontFamily': 'SuraSans-SemiBold', 'fontSize': '14px', 'marginBottom': '5px'}),
                dcc.DatePickerSingle(
                    id='fecha-inicio-grafico',
                    date=datetime.now() - timedelta(days=365),
                    display_format='DD/MM/YYYY',
                    style={'width': '100%', 'marginBottom': '10px'}
                ),
                html.Label("Hasta:", style={'fontFamily': 'SuraSans-SemiBold', 'fontSize': '14px', 'marginBottom': '5px'}),
                dcc.DatePickerSingle(
                    id='fecha-fin-grafico',
                    date=datetime.now(),
                    display_format='DD/MM/YYYY',
                    style={'width': '100%', 'marginBottom': '15px'}
                ),
                html.Div([
                    dbc.Button("1M", id="btn-1m", size="sm", outline=True, color="primary", style={'margin': '2px', 'width': '45px'}),
                    dbc.Button("3M", id="btn-3m", size="sm", outline=True, color="primary", style={'margin': '2px', 'width': '45px'}),
                    dbc.Button("6M", id="btn-6m", size="sm", outline=True, color="primary", style={'margin': '2px', 'width': '45px'}),
                    dbc.Button("YTD", id="btn-ytd", size="sm", outline=True, color="primary", style={'margin': '2px', 'width': '50px'}),
                    html.Br(),
                    dbc.Button("1Y", id="btn-1y", size="sm", outline=True, color="primary", active=True, style={'margin': '2px', 'width': '45px'}),
                    dbc.Button("3Y", id="btn-3y", size="sm", outline=True, color="primary", style={'margin': '2px', 'width': '45px'}),
                    dbc.Button("5Y", id="btn-5y", size="sm", outline=True, color="primary", style={'margin': '2px', 'width': '45px'}),
                    dbc.Button("Max", id="btn-max", size="sm", outline=True, color="primary", style={'margin': '2px', 'width': '50px'}),
                ], style={
                    'textAlign': 'left',
                    'backgroundColor': '#f8f9fa',
                    'padding': '10px',
                    'borderRadius': '5px',
                    'border': '1px solid #dee2e6'
                })
            ])
        ], width=3),
        
        dbc.Col([
            dcc.Graph(
                id='grafico-retornos-acumulados',
                config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToAdd': ['toImage'],
                    'toImageButtonOptions': {
                        'format': 'png',
                        'filename': 'retornos_acumulados',
                        'height': 800,
                        'width': 1200,
                        'scale': 2
                    }
                }
            )
        ], width=9)
    ], style={'marginBottom': '20px'})
], id="content-acumulada", style={'display': 'block'})

controles_anualizada = html.Div([
    html.H2("Rentabilidad Anualizada", 
            style={'fontFamily': 'SuraSans-SemiBold', 'marginBottom': '20px'}),
    
    html.P("Rentabilidades expresadas como tasa anual compuesta equivalente.", 
           style={'fontFamily': 'SuraSans-Regular', 'fontStyle': 'italic', 'marginBottom': '20px'}),
    
    dbc.Row([
        dbc.Col([
            html.Label("Moneda:", style={'fontFamily': 'SuraSans-SemiBold'}),
            dcc.Dropdown(
                id='moneda-selector-anualizada',
                options=[
                    {'label': 'Pesos Chilenos (CLP)', 'value': 'CLP'},
                    {'label': 'Dólares (USD)', 'value': 'USD'}
                ],
                value='CLP',
                style={'fontFamily': 'SuraSans-Regular'}
            )
        ], width=3),
        dbc.Col([
            html.Label([
                "Filtrar Fondos: ",
                html.Span("(sincronizado con otras pestañas)", 
                         style={'fontSize': '12px', 'color': '#0B2DCE', 'fontStyle': 'italic'})
            ], style={'fontFamily': 'SuraSans-SemiBold'}),
            dcc.Dropdown(
                id='fondos-selector-anualizada',
                options=[],
                value=[],
                multi=True,
                style={'fontFamily': 'SuraSans-Regular'}
            )
        ], width=9)
    ], style={'marginBottom': '20px'}),
    
    html.Div(id='tabla-rentabilidades-anualizada')
], id="content-anualizada", style={'display': 'none'})

controles_por_año = html.Div([
    html.H2("Rentabilidad por Año", 
            style={'fontFamily': 'SuraSans-SemiBold', 'marginBottom': '20px'}),
    
    html.P("Rentabilidades calculadas año calendario completo (enero a diciembre).", 
           style={'fontFamily': 'SuraSans-Regular', 'fontStyle': 'italic', 'marginBottom': '20px'}),
    
    dbc.Row([
        dbc.Col([
            html.Label("Moneda:", style={'fontFamily': 'SuraSans-SemiBold'}),
            dcc.Dropdown(
                id='moneda-selector-por-año',
                options=[
                    {'label': 'Pesos Chilenos (CLP)', 'value': 'CLP'},
                    {'label': 'Dólares (USD)', 'value': 'USD'}
                ],
                value='CLP',
                style={'fontFamily': 'SuraSans-Regular'}
            )
        ], width=3),
        dbc.Col([
            html.Label([
                "Filtrar Fondos: ",
                html.Span("(sincronizado con otras pestañas)", 
                         style={'fontSize': '12px', 'color': '#0B2DCE', 'fontStyle': 'italic'})
            ], style={'fontFamily': 'SuraSans-SemiBold'}),
            dcc.Dropdown(
                id='fondos-selector-por-año',
                options=[],
                value=[],
                multi=True,
                style={'fontFamily': 'SuraSans-Regular'}
            )
        ], width=9)
    ], style={'marginBottom': '20px'}),
    
    html.Div(id='tabla-rentabilidades-por-año')
], id="content-por-año", style={'display': 'none'})

# Layout principal con TODOS los componentes definidos
app.layout = html.Div([
   top_navbar,
   modal,
   modal_grafico,
   bottom_navbar,
   dbc.Container([
       tabs,
       html.Div([
           controles_acumulada,
           controles_anualizada,
           controles_por_año
       ], style={'padding': '30px'})
   ], fluid=True)
], style={'margin': '0', 'padding': '0'})

# Función para cargar y procesar datos
def cargar_datos_optimizado():
    try:
        posibles_rutas = [
            'data/rentabilidades.xlsx',          # Para deployment
            './data/rentabilidades.xlsx',       # Local relativa
            '../data/rentabilidades.xlsx',      # Backup
            'rentabilidades.xlsx'                # Si está en raíz
        ]
        
        ruta_archivo = None
        for ruta in posibles_rutas:
            if os.path.exists(ruta):
                ruta_archivo = ruta
                break
        
        if ruta_archivo is None:
            print("Error: No se encontró el archivo rentabilidades.xlsx")
            return None, None, [], []
        
        print(f"Cargando archivo desde: {ruta_archivo}")
        
        nombres_df = pd.read_excel(ruta_archivo, sheet_name='nombres', 
                                 header=None, engine='openpyxl')
        pesos_df = pd.read_excel(ruta_archivo, sheet_name='Pesos', 
                               skiprows=7, engine='openpyxl')
        dolares_df = pd.read_excel(ruta_archivo, sheet_name='Dolares', 
                                 skiprows=7, engine='openpyxl')
        
        fondos_raw = nombres_df.iloc[0, :].tolist()
        series_raw = nombres_df.iloc[2, :].tolist()
        
        fondos = [f for f in fondos_raw if pd.notna(f)]
        series = [s for s in series_raw if pd.notna(s)]
        
        nuevas_columnas = ['Dates'] + fondos
        
        if len(nuevas_columnas) == len(pesos_df.columns):
            pesos_df.columns = nuevas_columnas
            dolares_df.columns = nuevas_columnas
        else:
            print(f"Error: Longitud columnas no coincide")
            return None, None, [], []
        
        pesos_df['Dates'] = pd.to_datetime(pesos_df['Dates'])
        dolares_df['Dates'] = pd.to_datetime(dolares_df['Dates'])
        
        return pesos_df, dolares_df, fondos, series
        
    except Exception as e:
        print(f"Error cargando datos: {e}")
        return None, None, [], []

# Cargar datos al iniciar
pesos_df, dolares_df, fondos, series = cargar_datos_optimizado()

# Funciones de cálculo (mantener las mismas)
def calcular_rentabilidades(df, fondos, series):
   resultados = []
   fecha_actual = df['Dates'].max()
   
   for i, fondo in enumerate(fondos):
       if fondo in df.columns:
           serie = series[i] if i < len(series) else 'N/A'
           precios = df[['Dates', fondo]].dropna()
           
           if len(precios) > 0:
               precio_actual = precios[fondo].iloc[-1]
               
               rent_1m = calcular_rentabilidad_periodo(precios, 30, precio_actual)
               rent_3m = calcular_rentabilidad_periodo(precios, 90, precio_actual) 
               rent_ytd = calcular_rentabilidad_ytd(precios, precio_actual)
               rent_12m = calcular_rentabilidad_periodo(precios, 365, precio_actual)
               rent_3a = calcular_rentabilidad_periodo(precios, 1095, precio_actual)
               rent_5a = calcular_rentabilidad_periodo(precios, 1825, precio_actual)
               rent_itd = ((precio_actual / precios[fondo].iloc[0]) - 1) * 100
               
               resultados.append({
                   'Fondo': fondo,
                   'Serie': serie,
                   'TAC': np.random.uniform(0.5, 2.5),
                   '1 Mes': rent_1m,
                   '3 Meses': rent_3m,
                   'YTD': rent_ytd,
                   '12 Meses': rent_12m,
                   '3 Años': rent_3a,
                   '5 Años': rent_5a,
                   'ITD': rent_itd
               })
   
   return pd.DataFrame(resultados).round(2)

def calcular_rentabilidades_anualizadas(df, fondos, series):
    resultados = []
    
    for i, fondo in enumerate(fondos):
        if fondo in df.columns:
            serie = series[i] if i < len(series) else 'N/A'
            precios = df[['Dates', fondo]].dropna()
            
            if len(precios) > 0:
                precio_actual = precios[fondo].iloc[-1]
                precio_inicial = precios[fondo].iloc[0]
                fecha_inicial = precios['Dates'].iloc[0]
                fecha_actual = precios['Dates'].iloc[-1]
                
                años_transcurridos = (fecha_actual - fecha_inicial).days / 365.25
                
                if años_transcurridos > 0:
                    rent_anual_itd = (((precio_actual / precio_inicial) ** (1/años_transcurridos)) - 1) * 100
                else:
                    rent_anual_itd = 0
                
                rent_anual_1a = calcular_rentabilidad_anualizada_periodo(precios, 365)
                rent_anual_3a = calcular_rentabilidad_anualizada_periodo(precios, 1095)
                rent_anual_5a = calcular_rentabilidad_anualizada_periodo(precios, 1825)
                
                resultados.append({
                    'Fondo': fondo,
                    'Serie': serie,
                    '1 Año': rent_anual_1a,
                    '3 Años': rent_anual_3a,
                    '5 Años': rent_anual_5a,
                    'ITD': rent_anual_itd,
                    'Años Historial': round(años_transcurridos, 1)
                })
    
    return pd.DataFrame(resultados).round(2)

def calcular_rentabilidades_por_año(df, fondos, series):
    resultados = []
    años = sorted(df['Dates'].dt.year.unique())
    
    for i, fondo in enumerate(fondos):
        if fondo in df.columns:
            serie = series[i] if i < len(series) else 'N/A'
            precios = df[['Dates', fondo]].dropna()
            
            if len(precios) > 0:
                fila_resultado = {'Fondo': fondo, 'Serie': serie}
                
                for año in años:
                    datos_año = precios[precios['Dates'].dt.year == año]
                    
                    if len(datos_año) > 1:
                        precio_inicio = datos_año[fondo].iloc[0]
                        precio_fin = datos_año[fondo].iloc[-1]
                        rentabilidad = ((precio_fin / precio_inicio) - 1) * 100
                        fila_resultado[str(año)] = round(rentabilidad, 2)
                    else:
                        fila_resultado[str(año)] = np.nan
                
                resultados.append(fila_resultado)
    
    return pd.DataFrame(resultados)

def calcular_rentabilidad_periodo(precios, dias, precio_actual):
   fecha_objetivo = precios['Dates'].max() - timedelta(days=dias)
   precio_pasado = precios[precios['Dates'] >= fecha_objetivo]
   
   if len(precio_pasado) > 0:
       precio_inicial = precio_pasado.iloc[0, 1]
       return ((precio_actual / precio_inicial) - 1) * 100
   return np.nan

def calcular_rentabilidad_ytd(precios, precio_actual):
   año_actual = precios['Dates'].max().year
   inicio_año = precios[precios['Dates'].dt.year == año_actual]
   
   if len(inicio_año) > 0:
       precio_inicio_año = inicio_año.iloc[0, 1]
       return ((precio_actual / precio_inicio_año) - 1) * 100
   return np.nan

def calcular_rentabilidad_anualizada_periodo(precios, dias):
    fecha_objetivo = precios['Dates'].max() - timedelta(days=dias)
    datos_periodo = precios[precios['Dates'] >= fecha_objetivo]
    
    if len(datos_periodo) > 1:
        precio_inicial = datos_periodo.iloc[0, 1]
        precio_final = datos_periodo.iloc[-1, 1]
        fecha_inicial = datos_periodo['Dates'].iloc[0]
        fecha_final = datos_periodo['Dates'].iloc[-1]
        
        años = (fecha_final - fecha_inicial).days / 365.25
        if años > 0:
            return (((precio_final / precio_inicial) ** (1/años)) - 1) * 100
    return np.nan

def calcular_retornos_acumulados(df, fondos_seleccionados, fecha_inicio, fecha_fin):
    df_filtrado = df[(df['Dates'] >= fecha_inicio) & (df['Dates'] <= fecha_fin)].copy()
    
    if len(df_filtrado) == 0:
        return pd.DataFrame()
    
    retornos_data = {'Dates': df_filtrado['Dates']}
    
    for fondo in fondos_seleccionados:
        if fondo in df_filtrado.columns:
            precios = df_filtrado[fondo].dropna()
            if len(precios) > 0:
                precio_base = precios.iloc[0]
                retornos_acumulados = ((precios / precio_base) - 1) * 100
                retornos_data[fondo] = retornos_acumulados
    
    return pd.DataFrame(retornos_data)

def crear_grafico_retornos(df_retornos, fondos_seleccionados):
    if df_retornos.empty:
        return go.Figure().add_annotation(
            text="No hay datos para el período seleccionado",
            x=0.5, y=0.5, showarrow=False
        )
    
    fig = go.Figure()
    
    paleta_primaria = ['#24272A', '#0B2DCE', '#5A646E', '#98A4AE', '#FFE946']
    paleta_secundaria = [
        '#727272', '#52C599', '#CC9967', '#9B5634', '#D4BE7F', 
        '#3C86B4', '#A0A0A0', '#7FD4B3', '#D5AB80', '#C9805C', 
        '#9E3541', '#A8CDE2', '#C8C8C8', '#A3E1C2', '#E0C1A2', 
        '#D49A7D', '#DE9CA6', '#CBB363'
    ]
    
    num_fondos = len(fondos_seleccionados)
    colores_a_usar = paleta_primaria if num_fondos <= 5 else paleta_secundaria
    
    for i, fondo in enumerate(fondos_seleccionados):
        if fondo in df_retornos.columns:
            color_linea = colores_a_usar[i % len(colores_a_usar)]
            
            fig.add_trace(go.Scatter(
                x=df_retornos['Dates'],
                y=df_retornos[fondo],
                mode='lines',
                name=fondo,
                line=dict(color=color_linea, width=2),
                hovertemplate=f'<b>{fondo}</b><br>' +
                            'Fecha: %{x}<br>' +
                            'Retorno: %{y:.2f}%<extra></extra>'
            ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        title={
            'text': 'Retornos Acumulados',
            'x': 0.5,
            'y': 0.95,
            'font': {'family': 'SuraSans-SemiBold', 'size': 18, 'color': '#24272A'}
        },
        xaxis_title='Fecha',
        yaxis_title='Retorno Acumulado (%)',
        font={'family': 'SuraSans-Regular', 'color': '#24272A'},
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font={'family': 'SuraSans-Regular', 'size': 10}
        ),
        height=500,
        margin=dict(t=60, b=50, l=50, r=50),
        template='plotly_white',
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

# CALLBACKS OPTIMIZADOS

@callback(
    Output("info-modal", "is_open"),
    [Input("info-button", "n_clicks"), 
     Input("close-modal", "n_clicks")],
    [State("info-modal", "is_open")]
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# Callback para cambiar la visualización de pestañas
@callback(
    [Output("content-acumulada", "style"),
     Output("content-anualizada", "style"),
     Output("content-por-año", "style")],
    [Input("tabs", "active_tab")]
)
def update_tab_display(active_tab):
    styles = [{'display': 'none'}, {'display': 'none'}, {'display': 'none'}]
    
    if active_tab == "acumulada":
        styles[0] = {'display': 'block'}
    elif active_tab == "anualizada":
        styles[1] = {'display': 'block'}
    elif active_tab == "por_ano":
        styles[2] = {'display': 'block'}
    
    return styles

# Callback para inicializar opciones de fondos
@callback(
    [Output('fondos-selector-acumulada', 'options'),
     Output('fondos-selector-anualizada', 'options'),
     Output('fondos-selector-por-año', 'options')],
    [Input('tabs', 'active_tab')]
)
def inicializar_opciones_fondos(active_tab):
    if fondos:
        opciones = [{'label': fondo, 'value': fondo} for fondo in fondos]
        return opciones, opciones, opciones
    else:
        return [], [], []

# NUEVO CALLBACK PRINCIPAL: SINCRONIZACIÓN DE FONDOS ENTRE PESTAÑAS
@callback(
    [Output('fondos-selector-acumulada', 'value'),
     Output('fondos-selector-anualizada', 'value'),
     Output('fondos-selector-por-año', 'value')],
    [Input('fondos-selector-acumulada', 'value'),
     Input('fondos-selector-anualizada', 'value'),
     Input('fondos-selector-por-año', 'value')],
    prevent_initial_call=True
)
def sincronizar_fondos_entre_pestañas(fondos_acumulada, fondos_anualizada, fondos_por_año):
    """
    Sincroniza las selecciones de fondos entre todas las pestañas.
    Cuando cambias fondos en cualquier pestaña, se actualizan automáticamente en las otras.
    """
    ctx = dash.callback_context
    
    if not ctx.triggered:
        # Valores iniciales - primeros 5 fondos para acumulada y por año, 10 para anualizada
        if fondos:
            valores_acumulada = fondos[:5] if len(fondos) > 5 else fondos
            valores_anualizada = fondos[:10] if len(fondos) > 10 else fondos
            valores_por_año = fondos[:5] if len(fondos) > 5 else fondos
            return valores_acumulada, valores_anualizada, valores_por_año
        else:
            return [], [], []
    
    # Determinar qué selector fue el que cambió
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'fondos-selector-acumulada':
        # Si cambió acumulada, sincronizar con las otras dos
        return fondos_acumulada, fondos_acumulada, fondos_acumulada
    elif trigger_id == 'fondos-selector-anualizada':
        # Si cambió anualizada, sincronizar con las otras dos
        return fondos_anualizada, fondos_anualizada, fondos_anualizada
    elif trigger_id == 'fondos-selector-por-año':
        # Si cambió por año, sincronizar con las otras dos
        return fondos_por_año, fondos_por_año, fondos_por_año
    
    # Fallback - mantener valores actuales
    return fondos_acumulada, fondos_anualizada, fondos_por_año

# Callback SOLO para inicializar fechas por defecto
@callback(
    [Output('fecha-inicio-grafico', 'date'),
     Output('fecha-fin-grafico', 'date')],
    [Input('tabs', 'active_tab')]
)
def inicializar_fechas_grafico(active_tab):
    if pesos_df is not None:
        fecha_fin = pesos_df['Dates'].max()
        fecha_inicio = fecha_fin - timedelta(days=365)
        return fecha_inicio, fecha_fin
    else:
        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=365)
        return fecha_inicio, fecha_fin

# Callback para Rentabilidad Acumulada
@callback(
   Output('tabla-rentabilidades-acumulada', 'children'),
   [Input('moneda-selector-acumulada', 'value'),
    Input('fondos-selector-acumulada', 'value')]
)
def actualizar_tabla_acumulada(moneda, fondos_seleccionados):
   if not fondos_seleccionados or pesos_df is None:
       return html.P("Selecciona al menos un fondo", style={'fontFamily': 'SuraSans-Regular'})
   
   df_actual = pesos_df if moneda == 'CLP' else dolares_df
   
   fondos_filtrados = [f for f in fondos_seleccionados if f in fondos]
   series_filtradas = [series[fondos.index(f)] for f in fondos_filtrados if f in fondos]
   
   tabla_data = calcular_rentabilidades(df_actual, fondos_filtrados, series_filtradas)
   tabla_data['Moneda'] = moneda
   
   columnas_orden = ['Fondo', 'Serie', 'Moneda', 'TAC', '1 Mes', '3 Meses', 'YTD', '12 Meses', '3 Años', '5 Años', 'ITD']
   tabla_data = tabla_data[columnas_orden]
   
   return dash_table.DataTable(
       data=tabla_data.to_dict('records'),
       columns=[{"name": col, "id": col, "type": "numeric", "format": {"specifier": ".2f"}} 
               if col not in ['Fondo', 'Serie', 'Moneda'] else {"name": col, "id": col} 
               for col in tabla_data.columns],
       style_table={'overflowX': 'auto'},
       style_cell={
           'textAlign': 'center',
           'fontFamily': 'SuraSans-Regular',
           'fontSize': '12px'
       },
       style_header={
           'backgroundColor': '#000000',
           'color': 'white',
           'fontFamily': 'SuraSans-SemiBold',
           'fontWeight': 'bold'
       },
       style_data_conditional=[
           {
               'if': {'column_id': col, 'filter_query': f'{{{col}}} > 0'},
               'color': 'green'
           } for col in ['1 Mes', '3 Meses', 'YTD', '12 Meses', '3 Años', '5 Años', 'ITD']
       ] + [
           {
               'if': {'column_id': col, 'filter_query': f'{{{col}}} < 0'},
               'color': 'red'
           } for col in ['1 Mes', '3 Meses', 'YTD', '12 Meses', '3 Años', '5 Años', 'ITD']
       ]
   )

# Callback para Rentabilidad Anualizada
@callback(
   Output('tabla-rentabilidades-anualizada', 'children'),
   [Input('moneda-selector-anualizada', 'value'),
    Input('fondos-selector-anualizada', 'value')]
)
def actualizar_tabla_anualizada(moneda, fondos_seleccionados):
   if not fondos_seleccionados or pesos_df is None:
       return html.P("Selecciona al menos un fondo", style={'fontFamily': 'SuraSans-Regular'})
   
   df_actual = pesos_df if moneda == 'CLP' else dolares_df
   
   fondos_filtrados = [f for f in fondos_seleccionados if f in fondos]
   series_filtradas = [series[fondos.index(f)] for f in fondos_filtrados if f in fondos]
   
   tabla_data = calcular_rentabilidades_anualizadas(df_actual, fondos_filtrados, series_filtradas)
   tabla_data['Moneda'] = moneda
   
   columnas_orden = ['Fondo', 'Serie', 'Moneda', '1 Año', '3 Años', '5 Años', 'ITD', 'Años Historial']
   tabla_data = tabla_data[columnas_orden]
   
   return dash_table.DataTable(
       data=tabla_data.to_dict('records'),
       columns=[{"name": col, "id": col, "type": "numeric", "format": {"specifier": ".2f"}} 
               if col not in ['Fondo', 'Serie', 'Moneda'] else {"name": col, "id": col} 
               for col in tabla_data.columns],
       style_table={'overflowX': 'auto'},
       style_cell={
           'textAlign': 'center',
           'fontFamily': 'SuraSans-Regular',
           'fontSize': '12px'
       },
       style_header={
           'backgroundColor': '#000000',
           'color': 'white',
           'fontFamily': 'SuraSans-SemiBold',
           'fontWeight': 'bold'
       },
       style_data_conditional=[
           {
               'if': {'column_id': col, 'filter_query': f'{{{col}}} > 0'},
               'color': 'green'
           } for col in ['1 Año', '3 Años', '5 Años', 'ITD']
       ] + [
           {
               'if': {'column_id': col, 'filter_query': f'{{{col}}} < 0'},
               'color': 'red'
           } for col in ['1 Año', '3 Años', '5 Años', 'ITD']
       ]
   )

# Callback para Rentabilidad por Año
@callback(
   Output('tabla-rentabilidades-por-año', 'children'),
   [Input('moneda-selector-por-año', 'value'),
    Input('fondos-selector-por-año', 'value')]
)
def actualizar_tabla_por_año(moneda, fondos_seleccionados):
   if not fondos_seleccionados or pesos_df is None:
       return html.P("Selecciona al menos un fondo", style={'fontFamily': 'SuraSans-Regular'})
   
   df_actual = pesos_df if moneda == 'CLP' else dolares_df
   
   fondos_filtrados = [f for f in fondos_seleccionados if f in fondos]
   series_filtradas = [series[fondos.index(f)] for f in fondos_filtrados if f in fondos]
   
   tabla_data = calcular_rentabilidades_por_año(df_actual, fondos_filtrados, series_filtradas)
   tabla_data['Moneda'] = moneda
   
   columnas_base = ['Fondo', 'Serie', 'Moneda']
   años_columnas = [col for col in tabla_data.columns if col not in columnas_base]
   años_columnas.sort(reverse=True)
   columnas_orden = columnas_base + años_columnas
   
   tabla_data = tabla_data[columnas_orden]
   
   return dash_table.DataTable(
       data=tabla_data.to_dict('records'),
       columns=[{"name": col, "id": col, "type": "numeric", "format": {"specifier": ".2f"}} 
               if col not in ['Fondo', 'Serie', 'Moneda'] else {"name": col, "id": col} 
               for col in tabla_data.columns],
       style_table={'overflowX': 'auto'},
       style_cell={
           'textAlign': 'center',
           'fontFamily': 'SuraSans-Regular',
           'fontSize': '11px'
       },
       style_header={
           'backgroundColor': '#000000',
           'color': 'white',
           'fontFamily': 'SuraSans-SemiBold',
           'fontWeight': 'bold'
       },
       style_data_conditional=[
           {
               'if': {'column_id': col, 'filter_query': f'{{{col}}} > 0'},
               'color': 'green'
           } for col in años_columnas
       ] + [
           {
               'if': {'column_id': col, 'filter_query': f'{{{col}}} < 0'},
               'color': 'red'
           } for col in años_columnas
       ]
   )

# Callback para botones de período
@callback(
    [Output('fecha-inicio-grafico', 'date', allow_duplicate=True),
     Output('fecha-fin-grafico', 'date', allow_duplicate=True)],
    [Input('btn-1m', 'n_clicks'),
     Input('btn-3m', 'n_clicks'),
     Input('btn-6m', 'n_clicks'),
     Input('btn-ytd', 'n_clicks'),
     Input('btn-1y', 'n_clicks'),
     Input('btn-3y', 'n_clicks'),
     Input('btn-5y', 'n_clicks'),
     Input('btn-max', 'n_clicks')],
    prevent_initial_call=True
)
def actualizar_fechas_grafico(btn1m, btn3m, btn6m, btnytd, btn1y, btn3y, btn5y, btnmax):
    ctx = dash.callback_context
    if not ctx.triggered or pesos_df is None:
        return dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    fecha_fin = pesos_df['Dates'].max()
    
    if button_id == 'btn-1m':
        fecha_inicio = fecha_fin - timedelta(days=30)
    elif button_id == 'btn-3m':
        fecha_inicio = fecha_fin - timedelta(days=90)
    elif button_id == 'btn-6m':
        fecha_inicio = fecha_fin - timedelta(days=180)
    elif button_id == 'btn-ytd':
        fecha_inicio = pd.Timestamp(fecha_fin.year, 1, 1)
    elif button_id == 'btn-1y':
        fecha_inicio = fecha_fin - timedelta(days=365)
    elif button_id == 'btn-3y':
        fecha_inicio = fecha_fin - timedelta(days=1095)
    elif button_id == 'btn-5y':
        fecha_inicio = fecha_fin - timedelta(days=1825)
    elif button_id == 'btn-max':
        fecha_inicio = pesos_df['Dates'].min()
    else:
        return dash.no_update, dash.no_update
    
    return fecha_inicio, fecha_fin

# Callback para actualizar gráfico
@callback(
    Output('grafico-retornos-acumulados', 'figure'),
    [Input('moneda-selector-acumulada', 'value'),
     Input('fondos-selector-acumulada', 'value'),
     Input('fecha-inicio-grafico', 'date'),
     Input('fecha-fin-grafico', 'date')]
)
def actualizar_grafico_retornos(moneda, fondos_seleccionados, fecha_inicio, fecha_fin):
    if not fondos_seleccionados or pesos_df is None:
        fig_vacio = go.Figure()
        fig_vacio.add_annotation(
            text="Selecciona al menos un fondo para ver el gráfico",
            x=0.5, 
            y=0.5, 
            showarrow=False,
            font={'family': 'SuraSans-Regular', 'size': 16, 'color': '#666666'},
            xanchor='center',  
            yanchor='middle',
            xref='paper',  # ← AGREGAR ESTA LÍNEA
            yref='paper',  # ← AGREGAR ESTA LÍNEA
        ),
        fig_vacio.update_layout(
            plot_bgcolor='#f8f9fa',  # Gris claro
            paper_bgcolor='#f8f9fa',  # Gris claro
            xaxis=dict(
                showgrid=False,  # Sin líneas de cuadrícula
                showticklabels=False,  # Sin etiquetas
                zeroline=False,  # Sin línea de cero
                visible=False  # Ocultar completamente el eje
            ),
            yaxis=dict(
                showgrid=False,  # Sin líneas de cuadrícula
                showticklabels=False,  # Sin etiquetas
                zeroline=False,  # Sin línea de cero
                visible=False  # Ocultar completamente el eje
            ),
            margin=dict(t=20, b=20, l=20, r=20),
            height=500
        )
        return fig_vacio
    
    df_actual = pesos_df if moneda == 'CLP' else dolares_df
    
    df_retornos = calcular_retornos_acumulados(
        df_actual, fondos_seleccionados, 
        pd.to_datetime(fecha_inicio), pd.to_datetime(fecha_fin)
    )
    
    return crear_grafico_retornos(df_retornos, fondos_seleccionados)

# Callback para abrir/cerrar modal de gráfico
@callback(
    Output("modal-grafico", "is_open"),
    [Input("btn-pantalla-completa", "n_clicks")],
    [State("modal-grafico", "is_open")],
    prevent_initial_call=True
)
def toggle_modal_grafico(btn_open, is_open):
    if btn_open:
        return not is_open
    return is_open

# Callback para sincronizar gráfico del modal
@callback(
    Output('grafico-retornos-modal', 'figure'),
    [Input('grafico-retornos-acumulados', 'figure')],
    prevent_initial_call=True
)
def sincronizar_grafico_modal(figure):
    if figure and 'data' in figure and len(figure['data']) > 0:
        figure_modal = figure.copy()
        
        figure_modal['layout'].update({
            'height': 750,
            'margin': dict(t=100, b=80, l=20, r=20),
            'title': {
                'text': 'Retornos Acumulados - Vista Completa',
                'x': 0.5,
                'y': 0.95,
                'font': {'family': 'SuraSans-SemiBold', 'size': 26, 'color': '#24272A'}
            },
            'legend': {
                'orientation': 'h',
                'x': 0.5,
                'y': -0.15,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'family': 'SuraSans-Regular', 'size': 14},
                'bgcolor': 'rgba(255,255,255,0.9)',
                'bordercolor': 'rgba(0,0,0,0.1)',
                'borderwidth': 1
            },
            'xaxis': {
                'title': {'text': 'Fecha', 'font': {'size': 18}},
                'tickfont': {'size': 14}
            },
            'yaxis': {
                'title': {'text': 'Retorno Acumulado (%)', 'font': {'size': 18}},
                'tickfont': {'size': 14}
            },
            'plot_bgcolor': 'white',
            'paper_bgcolor': 'white'
        })
        
        return figure_modal
    
    # Si no hay datos, mostrar mensaje con fondo gris limpio
    fig_vacio = go.Figure()
    fig_vacio.add_annotation(
        text="Selecciona fondos para ver el gráfico",
        x=0.5, 
        y=0.5, 
        showarrow=False,
        font={'family': 'SuraSans-Regular', 'size': 20, 'color': '#666666'},
        xanchor='center',   
        yanchor='middle',
        xref='paper',  # ← AGREGAR ESTA LÍNEA
        yref='paper',  # ← AGREGAR ESTA LÍNEA
    )
    fig_vacio.update_layout(
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='#f8f9fa',
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            visible=False
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            visible=False
        ),
        margin=dict(t=20, b=20, l=20, r=20),
        height=750
    )
    return fig_vacio
    
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8050))
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run_server(debug=debug_mode, host='0.0.0.0', port=port)
