# Practica 1 --- Diagnostico y Limpieza de Datos
# Earthquake.csv (original, intacto) -> Earthquake_limpio.csv (nuevo)

# PRIMERA PARTE: Diagnostico --- Explora el dataset para identificar que necesita limpieza
# SEGUNDA PARTE: Limpieza --- Aplica las decisiones de limpieza justificadas
# NO modifica ni sobreescribe el archivo original

# ======================================================================================
# || IMPORTANTE: Para mayores justificaciones, visualizar el archivo Justificacion.md ||
# ======================================================================================



import pandas as pd # pandas para manejar toda la tabla de datos
import numpy as np # numpy lo usamos para poner NaN (datos faltantes)

from pathlib import Path # pathlib para armar las rutas de los archivos sin batallar


# Para que al imprimir tablas no se corten las columnas y se vea todo completo
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 150)

# Buscamos la carpeta donde esta guardado este mismo script
try:
    CARPETA = Path(__file__).parent # Aqui hubo problemas porque la ruta no la encontraba :(
except NameError:
    CARPETA = Path.cwd() # Pero si se soluciono de esta manera :)

RUTA_ORIGINAL = CARPETA / 'Earthquake.csv' # De donde leemos el original y donde guardamos el limpio
RUTA_LIMPIO = CARPETA / 'Earthquake_limpio.csv'

# ==========================
# || DIAGNOSTICO DE DATOS ||
# ==========================
# En toda esta parte NO se cambió nada del csv, solo "vemos" los datos para saber que hay que limpiar 
print('\nDIAGNOSTICO DE DATOS')

# Si el csv no existe, aventamos error y avisamos donde debe ir
if not RUTA_ORIGINAL.exists():
    raise FileNotFoundError(
        f"No se encontro el archivo: {RUTA_ORIGINAL}\n"
        "Coloca Earthquake.csv en la misma carpeta que este script."
    )

# Cargamos el csv a un DataFrame 
df = pd.read_csv(RUTA_ORIGINAL)

# Guardamos los totales del inicio para compararlos al final
filas_originales = len(df)
columnas_originales = len(df.columns)

# FORMA Y TIPOS DE DATO
# shape = cuantas filas y columnas hay
#  dtypes = de que tipo es cada columna numero, texto, etc
print('\n1. FORMA Y TIPOS DE DATO')
print('Filas y columnas:', df.shape)
print(df.dtypes)

# VALORES NULOS POR COLUMNA
# Cuenta datos faltantes de cada columna
print('\n2. VALORES NULOS POR COLUMNA')
print(df.isnull().sum())

# DUPLICADOS
# Revisa si hay filas repetidas o ids repetidos 
print('\n3. DUPLICADOS')
print('Filas completas duplicadas:', df.duplicated().sum())
print('IDs duplicados:', df['id'].duplicated().sum())

# DESCRIPCION VARIABLES NUMERICAS
# Resumen de los numeros minimo, maximo, promedio
# Aqui cachamos cosas raras las profundidades negativas
print('\n4. DESCRIBE - VARIABLES NUMERICAS')
print(df.describe())

# VALUE_COUNTS CATEGORICAS
# Cuenta cuantas veces aparece cada categoria
# Sirve para ver si hay categorias con poquitos registros
print('\n5. VALUE_COUNTS - VARIABLES CATEGORICAS')
columnas_categoricas_diag = ['magType', 'net', 'status', 'locationSource', 'magSource', 'type']
for col in columnas_categoricas_diag:
    print(df[col].value_counts())
    print()

# COMPARACION ENTRE COLUMNAS SIMILARES
# Vemos si una columna es copia de otra 
print('\n6. COMPARACION ENTRE COLUMNAS SIMILARES')
print('net == locationSource en todas las filas?', (df['net'] == df['locationSource']).all())
print('net == magSource en todas las filas?', (df['net'] == df['magSource']).all())

# FECHAS
# Convertimos a fecha SOLO para ver el rango aqui todavia no cambiamos nada
print('\n7. FECHAS')
fechas_diag = pd.to_datetime(df['time'])
print('Fecha minima:', fechas_diag.min())
print('Fecha maxima:', fechas_diag.max())

# VALORES UNICOS (revisar formato // inconsistencias)
# Muestra todos los valores distintos para identificar textos raros o mal escritos
print('\n8. VALORES UNICOS (revisar formato/inconsistencias)')
for col in columnas_categoricas_diag:
    print(col, ':', df[col].unique())







# =======================
# || LIMPIEZA DE DATOS ||
# =======================
# Aqui ahora si empezamos a modificar la tabla (ahora si viene lo chido)
print('LIMPIEZA DE DATOS')
print('Origen:', RUTA_ORIGINAL)
print(f'Filas originales: {filas_originales}')
print(f'Columnas originales: {columnas_originales}')

# 1. CONVIRTIENDO FECHAS A DATETIME
# time y updated venian como texto, las volvemos fechas reales
# utc=True: estandariza todo a la misma zona horaria
# errors='coerce': si hay una fecha invalida la vuelve NaT (fecha vacia) en vez de tronar
# tz_localize(None): quita la zona horaria para que no de problemas en graficas y modelos
print('\n1. CONVIRTIENDO FECHAS A DATETIME')
for col in ['time', 'updated']:
    df[col] = pd.to_datetime(df[col], utc=True, errors='coerce')
    df[col] = df[col].dt.tz_localize(None)

# Contamos cuantas fechas quedaron invalidas
nulos_fecha = int(df[['time', 'updated']].isna().sum().sum())
print(f'Valores de fecha invalidos encontrados: {nulos_fecha}')

# Si alguna fila quedo sin fecha valida mejor la quitamos (sin fecha no nos sirve)
df = df.dropna(subset=['time', 'updated'])
print('Filas eliminadas por fecha invalida:', filas_originales - len(df))

# 2. VERIFICANDO DUPLICADOS
# El diagnostico dijo que no habia pero lo checamos por si las dudas
print('\n2. VERIFICANDO DUPLICADOS')
antes = len(df)
df = df.drop_duplicates(subset='id', keep='first') # si hubiera ids repetidos nos quedamos con el primero
print('IDs duplicados eliminados:', antes - len(df))

# 3. NORMALIZANDO TEXTO EN COLUMNAS CATEGORICAS
# Quitamos espacios de mas y ponemos todo en minusculas
# para que "Texas" y "texas " no cuenten como cosas diferentes
print('\n3. NORMALIZANDO TEXTO EN COLUMNAS CATEGORICAS')
for col in ['id', 'place', 'net', 'magType', 'magSource']:
    df[col] = df[col].astype('string').str.strip() # strip = quita espacios del inicio y del final
    df[col] = df[col].replace('', np.nan) # si queda texto vacio lo dejamos como dato faltante

if 'locationSource' in df.columns:
    df['locationSource'] = df['locationSource'].astype('string').str.strip()
    df['locationSource'] = df['locationSource'].replace('', np.nan)

df['net'] = df['net'].str.lower()
df['magType'] = df['magType'].str.lower()
df['magSource'] = df['magSource'].str.lower()
print('Texto normalizado: sin espacios extremos y en minusculas.')

# 4. ELIMINANDO COLUMNAS REDUNDANTES y/o SIN INFORMACION
# locationSource es igualita a net -> sobra
# type solo dice "earthquake" en todas las filas -> no aporta nada
# status casi siempre dice "reviewed" -> tampoco aporta
print('\n4. ELIMINANDO COLUMNAS REDUNDANTES / SIN INFORMACION')
if 'locationSource' in df.columns:
    mask = df['net'].notna() & df['locationSource'].notna()
    igualdad = (df.loc[mask, 'net'] == df.loc[mask, 'locationSource']).mean()
    print(f'Igualdad net vs locationSource: {igualdad:.2%}')

    if igualdad > 0.999:
        df = df.drop(columns=['locationSource'])
        print('locationSource eliminada (identica a net).')
    else:
        print('locationSource NO es identica a net. Se conserva.')

if 'type' in df.columns:
    if df['type'].nunique() == 1: # nunique = cuantos valores distintos hay
        df = df.drop(columns=['type'])
        print('type eliminada (un solo valor unico).')
    else:
        print('type tiene multiples valores. Se conserva.')

if 'status' in df.columns:
    proporcion_reviewed = (df['status'] == 'reviewed').mean()
    print(f'Proporcion de reviewed en status: {proporcion_reviewed:.2%}')

    if proporcion_reviewed > 0.99:
        df = df.drop(columns=['status'])
        print('status eliminada (practicamente constante).')
    else:
        print('status tiene variacion. Se conserva.')

# 5. UNIFICANDO CATEGORIAS EN magType
# ml(texnet), mlv y mlr son lo mismo que ml (magnitud local),
# solo que cada red lo escribia diferente, asi que los juntamos en uno solo
print('\n5. UNIFICANDO CATEGORIAS EN magType')
conteos_antes = df['magType'].value_counts()
print('Antes de unificar:')
print(conteos_antes)

df['magType'] = df['magType'].replace({
    'ml(texnet)': 'ml',
    'mlv': 'ml',
    'mlr': 'ml'
})

conteos_despues = df['magType'].value_counts()
print()
print('Despues de unificar:')
print(conteos_despues)
print()
print('ml(texnet), mlv y mlr unificados como ml.')

# 6. FILTRANDO VALORES INCONSISTENTES
# Revisamos que latitud, longitud y magnitud tengan sentido fisico
# (una latitud de 999 no existe en el planeta por ejemplo)
print('\n6. FILTRANDO VALORES INCONSISTENTES')
antes = len(df)

df = df[df['latitude'].between(-90, 90)]
df = df[df['longitude'].between(-180, 180)]
df = df[df['mag'] > 0]

print(f'Filas eliminadas por lat/lon/mag fuera de rango: {antes - len(df)}')

# Las profundidades negativas NO las borramos (ver Justificacion.md),
# solo las contamos para dejarlo documentado
negativas = int((df['depth'] < 0).sum())
print(f'Profundidades negativas conservadas (ver justificacion): {negativas}')

# 7. RECLASIFICANDO CEROS PLACEHOLDER COMO DESCONOCIDO
# En estas columnas un cero no es un cero real "SEGÚN" significa la red no dió el dato
print('\n7. RECLASIFICANDO CEROS PLACEHOLDER COMO DESCONOCIDO')
columnas_con_ceros = ['magError', 'horizontalError', 'rms', 'magNst', 'dmin']

for col in columnas_con_ceros:
    ceros = int((df[col] == 0).sum())
    df.loc[df[col] == 0, col] = np.nan # cero -> NaN (desconocido)
    print(f'{col}: {ceros} ceros reclasificados como desconocido.')

# 8. IMPUTANDO VALORES NULOS CON LA MEDIANA
# Rellenamos los huecos con la mediana
# porque el promedio se deforma con valores extremos
print('\n8. IMPUTANDO VALORES NULOS CON LA MEDIANA')
columnas_a_imputar = [
    'nst', 'gap', 'dmin', 'rms',
    'magError', 'horizontalError', 'depthError', 'magNst'
]

for col in columnas_a_imputar:
    if col not in df.columns:
        continue

    df[col] = pd.to_numeric(df[col], errors='coerce') # por si algun numero vino como texto
    nulos_antes = int(df[col].isnull().sum())

    if nulos_antes > 0:
        mediana = df[col].median()

        if pd.isna(mediana): # caso raro si todo fuera nulo usamos 0 para no tronar
            mediana = 0.0

        df[col] = df[col].fillna(mediana) # fillna = rellena los huecos
        print(f'{col}: {nulos_antes} nulos imputados con mediana ({mediana:.4f}).')
    else:
        print(f'{col}: sin nulos, nada que imputar.')

# 9. CREANDO COLUMNAS clean PARA CATEGORIAS SEGURAS
# Hacemos copias de net, magSource y magType, pero las categorias con menos de
# 30 registros (y es bastante generoso jajja) las colocamos en "other".
# Asi las practicas futuras (ANOVA, KNN, etc.) no fallan con grupos chiquitos
print('\n9. CREANDO COLUMNAS clean PARA CATEGORIAS SEGURAS')
columnas_categoricas = ['net', 'magSource', 'magType']

for col in columnas_categoricas:
    if col not in df.columns:
        continue

    conteos = df[col].value_counts()
    categorias_validas = conteos[conteos >= 30].index # solo las que tienen 30 o mas registros
    df[col + '_clean'] = df[col].where(df[col].isin(categorias_validas), 'other') # las chiquitas -> "other"

    print()
    print(df[col + '_clean'].value_counts())

# 10. MARCANDO PROFUNDIDADES ESTIMADAS
# Cuando el USGS no sabe la profundidad exacta le pone 5 o 10 km por defecto
# Marcamos esos casos con true para saber cuales son "estimados" y cuales reales
print('\n10. MARCANDO PROFUNDIDADES ESTIMADAS')
df['profundidad_estimada'] = df['depth'].isin([5.0, 10.0])

total_estimadas = int(df['profundidad_estimada'].sum())
pct_estimada = df['profundidad_estimada'].mean() * 100
print(f'profundidad_estimada: {total_estimadas} filas marcadas ({pct_estimada:.1f}%).')

# 11. ORDENANDO POR FECHA
# Lo dejamos en orden cronologico para mayor orden 
print('\n11. ORDENANDO POR FECHA')
df = df.sort_values('time').reset_index(drop=True) # reset_index para que el indice quede 0,1,2,3 y asi
print('Dataset ordenado por time.')

# 12. GUARDANDO ARCHIVO LIMPIO
# Guardamos en un csv nuevo el original queda intacto
# utf-8-sig para los caracteres raros etc
print('\n12. GUARDANDO ARCHIVO LIMPIO')
df.to_csv(RUTA_LIMPIO, index=False, encoding='utf-8-sig') # index=False para no guardar la columna de indices
print('Guardado en:', RUTA_LIMPIO)
print('Archivo original SIN modificar:', RUTA_ORIGINAL)
print()
print('Filas finales:', len(df))
print('Columnas finales:', len(df.columns))