# Practica 2 --- Estadistica Descriptiva
# Earthquake_limpio.csv -> estadistica descriptiva, entidades y relaciones,
# algebra relacional y metricas de datos agrupados.


import pandas as pd
import numpy as np  
from pathlib import Path

# Tablas bonitas 
try:
    from tabulate import tabulate
    def mostrar(df_tabla, encabezado=''):
        if encabezado:
            print(encabezado)
        print(tabulate(df_tabla, headers='keys', tablefmt='github'))
except ImportError:
    def mostrar(df_tabla, encabezado=''):
        if encabezado:
            print(encabezado)
        print(df_tabla)

try:
    CARPETA = Path(__file__).parent
except NameError:
    CARPETA = Path.cwd()

RUTA_LIMPIO = CARPETA / 'Earthquake_limpio.csv'

# Carpetas para guardar resultados
CARPETA_IMG = CARPETA / 'img'
CARPETA_IMG.mkdir(exist_ok=True)


#Cargar el dataset limpio
print('\nEARTHQUAKE_LIMPIO.CSV')
# parse_dates para que time y updated ya entren como fechas y no como texto
df = pd.read_csv(RUTA_LIMPIO, parse_dates=['time', 'updated'])
print(f'Filas: {len(df)}  Columnas: {len(df.columns)}')


# Convierte el texto de 'place' en un pais, para tener una
# variable categorica nueva y poder agrupar por ella (Esto esta basado en el archivo data_analysis.org del material de referencia de github)
def categorize_pais(place: str) -> str:
    if 'Guatemala' in place: return 'GUATEMALA'
    if 'Honduras' in place: return 'HONDURAS'
    # Lugares mexicanos que no dicen "Mexico" en el texto
    if 'Revilla Gigedo' in place or 'Gulf of California' in place: return 'MEXICO'
    # Ojo aqui: "New Mexico" tambien termina en "Mexico", pero es EEUU
    if place.endswith('Mexico') and 'New Mexico' not in place: return 'MEXICO'
    if 'B.C.' in place or ', MX' in place: return 'MEXICO'
    return 'EEUU'   # Texas, CA, New Mexico, etc

df['pais'] = df['place'].apply(categorize_pais)

print('\n*CATEGORIA CREADA: pais')
mostrar(df['pais'].value_counts().rename_axis('pais').reset_index(name='conteo'))



print('\n1. ESTADISTICA DESCRIPTIVA (VARIABLES NUMERICAS)')
numericas = ['mag', 'depth', 'latitude', 'longitude', 'nst', 'gap',
             'dmin', 'rms', 'horizontalError', 'depthError', 'magError', 'magNst']
mostrar(df[numericas].describe().round(3), 'describe() general:')




print('\n2. LAS 10 FUNCIONES DE AGREGACION (mag y depth)')

def estadisticas_completas(serie):
    return pd.Series({
        'min': serie.min(),
        'max': serie.max(),
        'moda': serie.mode()[0],
        'conteo': serie.count(),
        'sumatoria': serie.sum(),   # en mag no tiene mucho sentido fisico es solo ejercicio de la funcion
        'media': serie.mean(),
        'varianza': serie.var(),
        'desv_estandar': serie.std(),
        'asimetria': serie.skew(),
        'kurtosis': serie.kurt()
    })

tabla_funcs = pd.DataFrame({
    'mag': estadisticas_completas(df['mag']),
    'depth': estadisticas_completas(df['depth'])
})
mostrar(tabla_funcs.round(3))




print('\n3. ESTADISTICA DESCRIPTIVA (VARIABLES CATEGORICAS)')
# conteos rapidos para ver cuantos sismos hay en cada categoria
for col in ['net_clean', 'magType_clean', 'pais']:
    tabla = df[col].value_counts().rename_axis(col).reset_index(name='conteo')
    mostrar(tabla, f'\n')



print('\n4. ENTIDADES Y RELACIONES')

print('Entidad SISMO (cada fila es un sismo)')
mostrar(df[['id', 'time', 'latitude', 'longitude', 'depth', 'mag']].head(5))  # solo 5 filas para no saturar la consola

print('\nEntidad PAIS (donde ocurrio) (creada con categorize_pais)')
mostrar(df['pais'].value_counts().rename_axis('pais').reset_index(name='sismos'))

redes = pd.DataFrame({
    'net_clean': ['tx', 'us', 'ci', 'other'],
    'nombre_red': ['TexNet (Texas)', 'USGS Red Nacional', 'CISN (California)', 'Otras redes']
})
print('\nEntidad RED_SISMICA (quien registra el sismo)')
mostrar(redes)

tipos_mag = pd.DataFrame({
    'magType_clean': ['ml', 'mb', 'mww', 'mb_lg', 'mw', 'mwr', 'other'],
    'descripcion': ['Magnitud local', 'Ondas de cuerpo', 'Momento sismico',
                    'Ondas Lg', 'Magnitud momento', 'Momento regional', 'Otros']
})
print('\nEntidad TIPO_MAGNITUD (con que escala se midio)')
mostrar(tipos_mag)

#Entidad: FUENTE_MAGNITUD
# Casi siempre coincide con RED_SISMICA pero hay casos donde una red
# registra y OTRA calcula la magnitud (ejemplo net=us con magSource=ci o slm)
fuentes = pd.DataFrame({
    'magSource_clean': ['tx', 'us', 'ci', 'other'],
    'nombre_fuente': ['TexNet', 'USGS', 'CISN', 'Otras fuentes (slm, etc.)']
})
print('\nEntidad FUENTE_MAGNITUD (quien calculo la magnitud (secundaria))')
mostrar(fuentes)
print(f'(Secundaria: difiere de la red en {(df["net"] != df["magSource"]).sum()} casos)')


# misma idea que categorize_pais, pero bajando un nivel (estados-regiones)
def categorize_region(place: str) -> str:
    if 'Texas' in place: return 'TEXAS'
    if 'New Mexico' in place: return 'NEW MEXICO'
    if 'B.C.' in place or 'Baja California' in place: return 'BAJA CALIFORNIA'
    if ', CA' in place: return 'CALIFORNIA'
    if 'Guatemala' in place: return 'GUATEMALA'
    if 'Honduras' in place: return 'HONDURAS'
    return 'MEXICO | OTRA'

df['region'] = df['place'].apply(categorize_region)
print('\nEntidad REGION (nivel mas detallado que PAIS (secundaria))')
mostrar(df['region'].value_counts().rename_axis('region').reset_index(name='sismos'))

# con esto la dimension temporal para agrupar por fecha
df['mes'] = df['time'].dt.to_period('M').astype(str)
print('\nEntidad MES (dimension temporal (secundaria))')
print(f'Meses distintos con datos: {df["mes"].nunique()}')

#Relaciones 1:N
# groupby + size = contar cuantos sismos le tocan a cada categoria
print('\nRELACION 1: un PAIS tiene muchos SISMOS')
mostrar(df.groupby('pais').size().rename('sismos_ocurridos').reset_index())

print('\nRELACION 2: una RED_SISMICA registra muchos SISMOS')
mostrar(df.groupby('net_clean').size().rename('sismos_registrados').reset_index())

print('\nRELACION 3: TIPO_MAGNITUD mide muchos SISMOS')
mostrar(df.groupby('magType_clean').size().rename('sismos_medidos').reset_index())

print('\nRELACION 4 (secundaria): una FUENTE_MAGNITUD calcula muchos SISMOS')
mostrar(df.groupby('magSource_clean').size().rename('sismos_calculados').reset_index())

print('\nRELACION 5 (secundaria): una REGION tiene muchos SISMOS')
mostrar(df.groupby('region').size().rename('sismos_en_region').reset_index())

print('\nRELACION 6 (secundaria): un MES contiene muchos SISMOS')
mostrar(df.groupby('mes').size().rename('sismos_en_mes').reset_index().head(5))

#JOIN unir el sismo con sus entidades en una sola tabla
print('\nJOIN: sismo + red + tipo + pais en una sola tabla')
# how='left' para conservar todos los sismos aunque alguna entidad no tenga coincidencia
df_join = df.merge(redes, on='net_clean', how='left') \
            .merge(tipos_mag, on='magType_clean', how='left')
mostrar(df_join[['id', 'mag', 'net_clean', 'nombre_red', 'magType_clean', 'descripcion', 'pais']].head(5))

print('\n(El diagrama de estas entidades y relaciones esta en Justificacion2.md)')



# Operaciones del algebra relacional con su resultados
print('\n5. ALGEBRA RELACIONAL')

#SELECCION: quedarse con las FILAS que cumplen una condicion
print('SELECCION: sismos con magnitud >= 6 (Considerados fuertes)')
fuertes = df[df['mag'] >= 6]
print(f'De {len(df)} sismos, solo {len(fuertes)} cumplen mag >= 6:') 
mostrar(fuertes[['time', 'mag', 'depth', 'pais']])

#PROYECCION: quedarse solo con algunas COLUMNAS
print('\nPROYECCION: solo columnas time, mag, depth, pais')
proyeccion = df[['time', 'mag', 'depth', 'pais']]
print(f'La tabla completa tiene {len(df.columns)} columnas, aplicando proyeccion dejamos     {proyeccion.shape[1]}:')
mostrar(proyeccion.head(5))

#UNION: juntar dos conjuntos de filas en uno solo
print('\nUNION: sismos de Guatemala + sismos de Honduras (Centroamerica)')
gt = df[df['pais'] == 'GUATEMALA']
hn = df[df['pais'] == 'HONDURAS']
union_centroamerica = pd.concat([gt, hn])   # pd.concat para "pegar" una tabla debajo de la otra
print(f'Guatemala ({len(gt)}) + Honduras ({len(hn)}) = {len(union_centroamerica)} filas.')

#JOIN: cruzar tablas por una columna en comun 
print('\nJOIN: sismo cruzado con nombre de red y descripcion de magnitud')
mostrar(df_join[['id', 'net_clean', 'nombre_red', 'magType_clean', 'descripcion']].head(5))

#AGRUPACION: resumir filas por categoria 
print('\nAGRUPACION: conteo y magnitud por pais')
mostrar(df.groupby('pais')['mag'].agg(['count', 'mean', 'max']).round(3))

#TRANSPOSICION: convertir filas en columnas y viceversa
print('\nTRANSPOSICION: describe() con las variables como filas')
mostrar(df[numericas].describe().T.round(3))   # la .T es la que voltea la tabla





print('\n6. METRICAS DE DATOS AGRUPADOS')

df['anio'] = df['time'].dt.year

por_pais_anio = df.groupby(['pais', 'anio']).agg(
    conteo_sismos=('mag', 'count'),
    mag_media=('mag', 'mean'),
    mag_min=('mag', 'min'),
    mag_max=('mag', 'max'),
    profundidad_media=('depth', 'mean')
).round(3).reset_index()
mostrar(por_pais_anio, 'Sismos por pais y anio')

por_red = df.groupby('net_clean').agg(
    conteo=('mag', 'count'),
    mag_media=('mag', 'mean'),
    mag_max=('mag', 'max'),
    profundidad_media=('depth', 'mean'),
    nst_media=('nst', 'mean')
).round(3)
mostrar(por_red, '\nMetricas por red sismica')

por_tipo = df.groupby('magType_clean').agg(
    conteo=('mag', 'count'),
    mag_media=('mag', 'mean'),
    profundidad_media=('depth', 'mean')
).round(3)
mostrar(por_tipo, '\nMetricas por tipo de magnitud')

# PIVOT con unstack
anual = df.groupby(['anio', 'pais']).size().unstack(fill_value=0)  # fill_value=0 para que los huecos salgan como 0 y no como NaN
mostrar(anual, '\nConteo anual por pais (pivot/unstack)')



print('\n7. BOXPLOT POR CATEGORIA')
try:
    import matplotlib
    matplotlib.use('Agg')   # sin abrir ventanas
    import matplotlib.pyplot as plt

    # by='pais' = una caja por cada pais para compararlas de un vistazo
    df.boxplot(by='pais', column=['mag'], figsize=(10, 6))
    plt.suptitle('')
    plt.title('Magnitud por pais')
    plt.savefig(CARPETA_IMG / 'boxplot_pais.png')
    plt.close()

    df.boxplot(by='net_clean', column=['mag'], figsize=(10, 6))
    plt.suptitle('')
    plt.title('Magnitud por red sismica')
    plt.savefig(CARPETA_IMG / 'boxplot_red.png')
    plt.close()

    print('Boxplots guardados en img/boxplot_pais.png e img/boxplot_red.png')
except ImportError:
    print('matplotlib no instalado')