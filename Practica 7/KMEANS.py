# Practica 7 --- Agrupamiento de Datos (Clustering)
# descubrir grupos naturales con K-Means, sin usar etiquetas
# caracteristicas: las mismas 7 de registro de la Practica 6 sin lat/lon, porque
# el pais sale de la geografia (place), y agrupar por geografia para luego comparar
# contra pais seria redescubrir el mapa en vez de la estructura de los datos

# k-means a mano (centroides, asignar al mas cercano, recalcular, converger) aqui va como
# verificacion contra sklearn

# scikit-learn: pip install scikit-learn

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib
matplotlib.use('Agg')   

import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

try:
    CARPETA = Path(__file__).parent
except NameError:
    CARPETA = Path.cwd()

RUTA_LIMPIO = CARPETA / 'Earthquake_limpio.csv'
CARPETA_IMG = CARPETA / 'Graficas'   
CARPETA_IMG.mkdir(exist_ok=True)

df = pd.read_csv(RUTA_LIMPIO, parse_dates=['time'])

# pais se recrea SOLO para la evaluacion externa (la tabla cruzada),
# el clustering nunca lo ve
def categorize_pais(place: str) -> str:
    if 'Guatemala' in place: return 'GUATEMALA'
    if 'Honduras' in place: return 'HONDURAS'
    if 'Revilla Gigedo' in place or 'Gulf of California' in place: return 'MEXICO'
    if place.endswith('Mexico') and 'New Mexico' not in place: return 'MEXICO'
    if 'B.C.' in place or ', MX' in place: return 'MEXICO'
    return 'EEUU'

df['pais'] = df['place'].apply(categorize_pais)

# aqui no se excluye a honduras ni se parte train/test, el clustering no usa etiquetas
# ni predice, solo describe
FEATURES = ['depth', 'mag', 'nst', 'gap', 'dmin', 'rms', 'magNst']
X = df[FEATURES]

# k-means se basa en distancias, sin escalar el gap se come todo
scaler = StandardScaler()
X_s = scaler.fit_transform(X)




# BARRIDO DE K, codo (inercia) y silhouette, para elegir con evidencia
print('\n1. BARRIDO DE K')
ks = list(range(2, 9))
inercias = []
silhouettes = []
for k in ks:
    km = KMeans(n_clusters=k, n_init=10, random_state=42)
    etiquetas = km.fit_predict(X_s)
    # con casi 8000 puntos el silhouette completo se comeria media memoria, se calcula
    # sobre una muestra de 2000
    sil = silhouette_score(X_s, etiquetas, sample_size=2000, random_state=42)
    inercias.append(km.inertia_)
    silhouettes.append(sil)
    print(f'k={k}: inercia={km.inertia_:.1f} | silhouette={sil:.4f}')

mejor_k = ks[int(np.argmax(silhouettes))]
print(f'\nel k elegido por silhouette es {mejor_k}')
print('la inercia siempre baja al subir k, por eso no se elige con ella sola: su grafica es para buscar el codo')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12,5))
ax1.plot(ks, inercias, marker='o', color='tab:blue')
ax1.set_title('Inercia contra k (buscando el codo)')
ax1.set_xlabel('k')
ax1.set_ylabel('inercia')
ax1.grid(alpha=0.3)
ax2.plot(ks, silhouettes, marker='o', color='tab:green')
ax2.set_title('Silhouette contra k')
ax2.set_xlabel('k')
ax2.set_ylabel('silhouette')
ax2.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(CARPETA_IMG / 'kmeans_barrido_k.png')
plt.close()
print('kmeans_barrido_k.png guardado')





print('\n2. MODELO FINAL')
modelo = KMeans(n_clusters=mejor_k, n_init=10, random_state=42)
df['cluster'] = modelo.fit_predict(X_s)

sil_final = silhouette_score(X_s, df['cluster'], sample_size=2000, random_state=42)
print(f'inercia final: {modelo.inertia_:.1f} | silhouette final: {sil_final:.4f}')
print('tamanos de cluster:')
print(df['cluster'].value_counts().sort_index())

# evaluacion externa: contra la etiqueta que si teniamos, como lectura y no como verdad
print('\ntabla cruzada pais x cluster:')
print(pd.crosstab(df['pais'], df['cluster'], margins=True))

# perfil de cada cluster: que es cada grupo 
print('\nperfil de cada cluster (promedios):')
print(df.groupby('cluster')[FEATURES].mean().round(2))





print('\n3. DISPERSION POR CLUSTER')
colores = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray']
mag_v = df['mag'].values
depth_v = df['depth'].values

plt.figure(figsize=(9,6))
for c in sorted(df['cluster'].unique()):
    mask = (df['cluster'] == c).values
    plt.scatter(mag_v[mask], depth_v[mask], s=8, alpha=0.4, label=f'cluster {c}', color=colores[c % len(colores)])
# los centroides reales viven en 7 dimensiones, aqui se dibuja donde cae su promedio
# de mag y depth, para tenerlos a la vista en este plano
medios2d = df.groupby('cluster')[['mag', 'depth']].mean()
plt.scatter(medios2d['mag'], medios2d['depth'], marker='X', s=120,
            color='black', label='centroide (proyeccion)')
plt.title(f'Sismos agrupados por K-Means (k={mejor_k}) en el plano mag-depth')
plt.xlabel('mag')
plt.ylabel('depth')
plt.legend()
plt.tight_layout()
plt.savefig(CARPETA_IMG / 'kmeans_clusters_mag_depth.png')
plt.close()
print('kmeans_clusters_mag_depth.png guardado')



# K-MEANS A MANO COMO VERIFICACION 
print('\n4. K-MEANS A MANO VS SKLEARN')

def euclidean_distance(p_1, p_2):
    return np.sqrt(np.sum((p_2 - p_1) ** 2))

def scatter_iter(labels_act, nombre_png, titulo):
    plt.figure(figsize=(9,6))
    for c in np.unique(labels_act):
        mask = labels_act == c
        plt.scatter(mag_v[mask], depth_v[mask], s=8, alpha=0.4, label=f'cluster {c}', color=colores[c % len(colores)])
    plt.title(titulo)
    plt.xlabel('mag')
    plt.ylabel('depth')
    plt.legend()
    plt.tight_layout()
    plt.savefig(CARPETA_IMG / nombre_png)
    plt.close()

# centroides, asignar al mas cercano, recalcular, repetir;
# escrita con numpy porque con ciclos puros y 7893 puntos si tardaria de mas
rng = np.random.default_rng(42)
centroides = X_s[rng.choice(len(X_s), size=mejor_k, replace=False)].copy()
labels_man = np.full(len(X_s), -1)
for t in range(50):
    dists = np.sqrt(((X_s[:, None, :] - centroides[None, :, :]) ** 2).sum(-1))
    nuevos = np.argmin(dists, axis=1)
    if t == 0:
        scatter_iter(nuevos, 'kmeans_iter_inicio.png', f'K-Means a mano, iteracion 0 (k={mejor_k})')
        print('kmeans_iter_inicio.png guardado')
    prev = labels_man
    labels_man = nuevos
    for c in range(mejor_k):
        if (nuevos == c).any():
            centroides[c] = X_s[nuevos == c].mean(axis=0)
        # si un cluster queda vacio, su centroide se queda donde estaba: no hay promedio que sacar
    if np.array_equal(labels_man, prev):
        break

scatter_iter(labels_man, 'kmeans_iter_final.png', f'K-Means a mano, convergencia en iteracion {t} (k={mejor_k})')
print('kmeans_iter_final.png guardado')

inercia_man = ((X_s - centroides[labels_man]) ** 2).sum()
print(f'inercia K-Means a mano: {inercia_man:.1f}')
print(f'inercia sklearn:        {modelo.inertia_:.1f}')
print('deben quedar cercanas, si sklearn gana por poco es por su inicializacion k-means++ y sus 10 arranques')




print('\Conclusion:')
print(f'k elegido por silhouette: {mejor_k} | silhouette final: {sil_final:.4f}')
print('los clusters se compararon contra pais en la tabla cruzada y se perfilaron con promedios,')
print('la lectura esperada es que los grupos sigan regimenes (profundos vs someros) y no fronteras')
print('PARA MAYOR DETALLE VER: Justificacion7.md')