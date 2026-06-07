import json
import requests
import pandas as pd
import matplotlib.pyplot as plt


BCRA_TOKEN = "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE4MTE2MTkyMTMsInR5cGUiOiJleHRlcm5hbCIsInVzZXIiOiJjYXJvLmNhbmRlbGFtYXJ0aW5hQGdtYWlsLmNvbSJ9.TgLrN2ZOI7BlWiG9qk0GmF0m5iBaGkGDRdr897i-CB1e0FKiqC5i2GzCXaNUS_OGPB5v9IWyBMKgh97ITx7cLA"
FRED_KEY   = "7af625efe6c4bcc93848631174da493d"

FECHA_INICIO = "2016-12-01"
FECHA_FIN    = "2024-12-31"

def llamar_api(url, headers=None):
    respuesta = requests.get(url, headers=headers)
    if respuesta.status_code == 200:
       print(f"Conexión exitosa: {url[:50]}...")
       return respuesta.json()

#FRED
url_prueba = f"https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCSL&api_key={FRED_KEY}&file_type=json&observation_start={FECHA_INICIO}&observation_end={FECHA_FIN}"

datos_prueba = llamar_api(url_prueba)

if datos_prueba:
    print(f"Cantidad de registros obtenidos: {len(datos_prueba['observations'])}")
    print(f"Primer registro: {datos_prueba['observations'][0]}")

#BCRA
url_bcra = f"https://api.estadisticasbcra.com/usd_of?desde={FECHA_INICIO}&hasta={FECHA_FIN}"
headers_bcra = {"Authorization": f"Bearer {BCRA_TOKEN}"}

datos_bcra = llamar_api(url_bcra, headers=headers_bcra)

if datos_bcra:
    print(f"Cantidad de registros obtenidos: {len(datos_bcra)}")
    print(f"Primer registro: {datos_bcra[0]}")

#INDEC
url_ipc_arg = f"https://apis.datos.gob.ar/series/api/series/?ids=148.3_INIVELNAL_DICI_M_26&format=json&start_date={FECHA_INICIO}&end_date={FECHA_FIN}&limit=500"

datos_ipc_arg = llamar_api(url_ipc_arg)

if datos_ipc_arg:
    registros = datos_ipc_arg['data']
    print(f"Cantidad de registros obtenidos: {len(registros)}")
    print(f"Primer registro: {registros[0]}")
    print(f"Último registro: {registros[-1]}")

#Balanza comercial
url_balanza = f"https://apis.datos.gob.ar/series/api/series/?ids=77.1_IET_0_A_25,78.3_IIT_0_A_25&format=json&start_date={FECHA_INICIO}&end_date={FECHA_FIN}&limit=500&collapse=year&collapse_aggregation=sum"

datos_balanza = llamar_api(url_balanza)

if datos_balanza:
    registros = datos_balanza['data']
    print(f"Cantidad de registros: {len(registros)}")
    print(f"Primer registro: {registros[0]}")
    print(f"Último registro: {registros[-1]}")

#DATAFRAME DE BC
df_balanza = pd.DataFrame(
    datos_balanza['data'],
    columns=['fecha', 'exportaciones', 'importaciones']
)

df_balanza['fecha'] = pd.to_datetime(df_balanza['fecha'])

# Calcular balanza
df_balanza['balanza'] = df_balanza['exportaciones'] - df_balanza['importaciones']
print(df_balanza)

#TCN (BCRA)
url_bcra = f"https://api.estadisticasbcra.com/usd_of?desde={FECHA_INICIO}&hasta={FECHA_FIN}"
headers_bcra = {"Authorization": f"Bearer {BCRA_TOKEN}"}

datos_tcn = llamar_api(url_bcra, headers=headers_bcra)

if datos_tcn:
    print(f"Cantidad de registros: {len(datos_tcn)}")
    print(f"Primer registro: {datos_tcn[0]}")
    print(f"Último registro: {datos_tcn[-1]}")
df_tcn = pd.DataFrame(datos_tcn)
df_tcn.columns = ['fecha', 'tcn']

df_tcn['fecha'] = pd.to_datetime(df_tcn['fecha'])
df_tcn['año'] = df_tcn['fecha'].dt.year
df_tcn = df_tcn[df_tcn['fecha'].dt.year >= 2017]

df_tcn_anual = df_tcn.groupby('año')['tcn'].mean().reset_index()
df_tcn_anual.columns = ['año', 'tcn_promedio']

print(df_tcn_anual)

#CPI (EEUU)
url_fred = f"https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCSL&api_key={FRED_KEY}&file_type=json&observation_start={FECHA_INICIO}&observation_end={FECHA_FIN}"

datos_cpi_eeuu = llamar_api(url_fred)

if datos_cpi_eeuu:
   
    df_cpi_eeuu = pd.DataFrame(datos_cpi_eeuu['observations'])[['date', 'value']]
    df_cpi_eeuu.columns = ['fecha', 'cpi_eeuu']
    df_cpi_eeuu['fecha'] = pd.to_datetime(df_cpi_eeuu['fecha'])
    df_cpi_eeuu['cpi_eeuu'] = pd.to_numeric(df_cpi_eeuu['cpi_eeuu'])
    
#promedio anual
    df_cpi_eeuu['año'] = df_cpi_eeuu['fecha'].dt.year
    df_cpi_eeuu_anual = df_cpi_eeuu.groupby('año')['cpi_eeuu'].mean().reset_index()
    
    print(df_cpi_eeuu_anual)

# IPC (ARG)
url_ipc_arg = f"https://apis.datos.gob.ar/series/api/series/?ids=148.3_INIVELNAL_DICI_M_26&format=json&start_date={FECHA_INICIO}&end_date={FECHA_FIN}&limit=500"

datos_ipc_arg = llamar_api(url_ipc_arg)

if datos_ipc_arg:
    df_ipc_arg = pd.DataFrame(datos_ipc_arg['data'], columns=['fecha', 'ipc_arg'])
    df_ipc_arg['fecha'] = pd.to_datetime(df_ipc_arg['fecha'])
    
#promedio anual
    df_ipc_arg['año'] = df_ipc_arg['fecha'].dt.year
    df_ipc_arg_anual = df_ipc_arg.groupby('año')['ipc_arg'].mean().reset_index()
    
    print(df_ipc_arg_anual)

#UNIR DATAFRAMES
df_tcr = df_tcn_anual.merge(df_cpi_eeuu_anual, on='año')
df_tcr = df_tcr.merge(df_ipc_arg_anual, on='año')

# Calcular TCR
df_tcr['tcr'] = df_tcr['tcn_promedio'] * (df_tcr['cpi_eeuu'] / df_tcr['ipc_arg'])

df_final = df_tcr.merge(df_balanza, left_on='año', right_on=df_balanza['fecha'].dt.year)
df_final = df_final.drop(columns=['fecha'])

print(df_final)

#gráfico de TCR vs BC

df_final_grafico = df_final[df_final['año'] <= 2023]

fig, ax1 = plt.subplots(figsize=(12, 6))

ax1.plot(df_final_grafico['año'], df_final_grafico['tcr'], color='steelblue', marker='o', label='TCR')
ax1.set_xlabel('Año')
ax1.set_ylabel('Tipo de Cambio Real', color='steelblue')
ax1.tick_params(axis='y', labelcolor='steelblue')

ax2 = ax1.twinx()
ax2.bar(df_final_grafico['año'], df_final_grafico['balanza'], color='coral', alpha=0.5, label='Balanza Comercial')
ax2.set_ylabel('Balanza Comercial (millones USD)', color='coral')
ax2.tick_params(axis='y', labelcolor='coral')
ax2.axhline(0, color='red', linestyle='--', linewidth=0.8)

plt.title('Tipo de Cambio Real vs Balanza Comercial (2017-2023)')
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')
plt.tight_layout()
plt.show()

