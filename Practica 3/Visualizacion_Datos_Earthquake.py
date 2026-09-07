# Practica 3 Visualizacion de Datos

import pandas as pd
import matplotlib

matplotlib.use('Agg')   #para que no abrir ventanas

import matplotlib.pyplot as plt
from pathlib import Path

try:
    CARPETA = Path(__file__).parent
except NameError:
    CARPETA = Path.cwd()

RUTA_LIMPIO = CARPETA / 'Earthquake_limpio.csv' # Igual, buscar el csv de manera automatica en la carpeta
GRAFICAS = CARPETA / 'Graficas' # todo se guarda en en la carpeta de "Graficas"
GRAFICAS.mkdir(exist_ok=True)

df = pd.read_csv(RUTA_LIMPIO, parse_dates=['time'])
print(f'Filas: {len(df)}  Columnas: {len(df.columns)}')

# Aqui se reutiliza la funcion de la practica 2 es para el mapa y las barras
def categorize_pais(place: str) -> str:
    if 'Guatemala' in place: return 'GUATEMALA'
    if 'Honduras' in place: return 'HONDURAS'
    if 'Revilla Gigedo' in place or 'Gulf of California' in place: return 'MEXICO'
    if place.endswith('Mexico') and 'New Mexico' not in place: return 'MEXICO'
    if 'B.C.' in place or ', MX' in place: return 'MEXICO'
    return 'EEUU'

df['pais'] = df['place'].apply(categorize_pais)

# diccionario de colores para la grafica de dispersion y de barras, mas que nada para que se vea bien y los colores sean coherentes
colores_pais = {'EEUU': 'tab:blue', 'MEXICO': 'tab:green',
                'GUATEMALA': 'tab:orange', 'HONDURAS': 'tab:red'}


# 1. HISTOGRAMAS con ciclo para no escribir lo mismo 4 veces
print('\n1. HISTOGRAMAS')
colores_hist = {'mag': 'steelblue', 'depth': 'seagreen',
                'nst': 'mediumpurple', 'rms': 'darkorange'}
for col in ['mag', 'depth', 'nst', 'rms']:
    plt.figure(figsize=(8,5))
    # con 25 barras se ve bien, probe con 50 y quedaba muy cargado
    plt.hist(df[col], bins=25, color=colores_hist[col], edgecolor='black')
    plt.title(f'Histograma de {col}')
    plt.xlabel(col)
    plt.ylabel('Cantidad sismos')
    plt.savefig(GRAFICAS / f'hist_{col}.png')
    plt.close()
    print(f'hist_{col}.png')


# 2. PASTELES solo categorias con suficientes datos
print('\n2. PASTELES')
for col in ['pais', 'net_clean']:
    conteos = df[col].value_counts()
    conteos = conteos[conteos >= 30] # las categorias con poquitos sismos en el pastel ni se ven asi que bye
    plt.figure(figsize=(7,7))
    plt.pie(conteos, labels=conteos.index, autopct='%1.1f%%', textprops={'fontsize': 12}) #para agrandar un poco el texto porque estaba un poco chico al principio
    plt.title(f'Porcentaje de sismos por {col}')
    plt.savefig(GRAFICAS / f'pastel_{col}.png')
    plt.close()
    print(f'pastel_{col}.png')


# 3. DISPERSION: latitud vs longitud
print('\n3. MAPA (DISPERSION)')
plt.figure(figsize=(10,7))
for pais in colores_pais:
    parte = df[df['pais'] == pais]
    # puntos chiquitos y con alpha, porque son casi 8000 y si no se hace una mancha no tan legible para interpretacion
    plt.scatter(parte['longitude'], parte['latitude'], s=8, alpha=0.5, label=pais, color=colores_pais[pais])
plt.title('Sismos por ubicacion')
plt.xlabel('Longitud')
plt.ylabel('Latitud')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(GRAFICAS / 'Mapa.png')
plt.close()
print('Mapa.png')


# 4. BARRAS sismos por anio
print('\n4. BARRAS POR ANIO')
df['anio'] = df['time'].dt.year
por_anio = df['anio'].value_counts().sort_index()
plt.figure(figsize=(8,5))
#color distinto por anio para distinguirlas mejor
colores_anio = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red',
                'tab:purple', 'tab:brown', 'tab:pink']
plt.bar(por_anio.index.astype(str), por_anio.values, color=colores_anio[:len(por_anio)])
plt.title('Sismos por año')
plt.xlabel('año')
plt.ylabel('Cantidad sismos')
plt.savefig(GRAFICAS / 'Barras_anio.png')
plt.close()
print('Barras_anio.png  (OJO: 2026 sale bajo porque el anio esta incompleto)')


# 5. BARRAS: magnitud media por pais
print('\n5. BARRAS MAGNITUD MEDIA')
mag_media = df.groupby('pais')['mag'].mean()
plt.figure(figsize=(8,5))
# cada pais con su propio color, igual que en el mapa
# (EEUU azul, MEXICO verde, GUATEMALA naranja, HONDURAS rojo)
plt.bar(mag_media.index, mag_media.values, color=[colores_pais[p] for p in mag_media.index])
plt.title('Magnitud media por pais')
plt.ylabel('magnitud media')
plt.savefig(GRAFICAS / 'Barras_mag_pais.png')
plt.close()
print('Barras_mag_pais.png')


# 6. LINEA: sismos por mes, para ver la tendencia en el tiempo
print('\n6. LINEA POR MES')
por_mes = df.groupby(df['time'].dt.to_period('M')).size()
plt.figure(figsize=(10,5))
plt.plot(por_mes.values, marker='.', markersize=3, linewidth=0.8)
# con 80 meses las etiquetas se amontonan, pongo una cada 12
etiquetas = [str(m) for m in por_mes.index]
plt.xticks(range(0, len(por_mes), 12), etiquetas[::12], rotation=90)
plt.title('Sismos por mes')
plt.ylabel('Cantidad sismos')
plt.tight_layout()
plt.savefig(GRAFICAS / 'Linea_mes.png')
plt.close()
print('Linea_mes.png')

#Este tipo de diagramas se hicieron en la materia de "Programacion basica", asi que se necesito recordar conceptos jajaja

print('\nTodas las graficas quedaron en la carpeta de "Graficas"')