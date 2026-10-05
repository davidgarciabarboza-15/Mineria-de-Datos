# Practica 6 Clasificacion de Datos
# si no tienes scikit-learn: pip install scikit-learn

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter
import matplotlib
matplotlib.use('Agg')   # como siempre, para que no abra ventanas
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split, cross_val_score   #
from sklearn.pipeline import make_pipeline   # scaler y modelo juntos, sin fugas entre folds
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

try:
    CARPETA = Path(__file__).parent
except NameError:
    CARPETA = Path.cwd()

RUTA_LIMPIO = CARPETA / 'Earthquake_limpio.csv'
CARPETA_IMG = CARPETA / 'Graficas' 
CARPETA_IMG.mkdir(exist_ok=True)

df = pd.read_csv(RUTA_LIMPIO, parse_dates=['time'])

# (si no mal recuerdo) cuarta practica que usa esta funcion
def categorize_pais(place: str) -> str:
    if 'Guatemala' in place: return 'GUATEMALA'
    if 'Honduras' in place: return 'HONDURAS'
    if 'Revilla Gigedo' in place or 'Gulf of California' in place: return 'MEXICO'
    if place.endswith('Mexico') and 'New Mexico' not in place: return 'MEXICO'
    if 'B.C.' in place or ', MX' in place: return 'MEXICO'
    return 'EEUU'

df['pais'] = df['place'].apply(categorize_pais)

# HONDURAS se excluye de la clasificacion con solo 34 sismos, ningun vecino votaria
# jamas por esa clase y el modelo nomas se la tragaria, queda documentado en el .md
df = df[df['pais'] != 'HONDURAS'].copy()
print(f'filas sin HONDURAS: {len(df)} (se excluyo por tener apenas 34 sismos)')

FEATURES = ['depth', 'mag', 'nst', 'gap', 'dmin', 'rms', 'magNst']
X = df[FEATURES]
y = df['pais']

# particion 70/30 estratificada y con semilla
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, stratify=y, random_state=42)


# 1 POR QUE ESCALAR el mismo KNN con y sin StandardScaler
# CAMBIO: esta comparacion tambien se decide con validacion cruzada SOLO sobre train,
# el test se guarda virgen para una unica evaluacion al final
print('\n1. CON Y SIN ESCALADO')
cv_sin = cross_val_score(KNeighborsClassifier(n_neighbors=5), X_train, y_train, cv=5)
pipe_con = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=5))
cv_con = cross_val_score(pipe_con, X_train, y_train, cv=5)
acc_sin = cv_sin.mean()
acc_con = cv_con.mean()
print(f'accuracy CV sin escalar:  {acc_sin:.4f}')
print(f'accuracy CV con escalado: {acc_con:.4f}')
print('knn vive de distancias: sin escalar, el gap (0-360) aplasta al dmin (0-8) y demas')


# 2. BARRIDO DE K, elegir k con evidencia 
# el k se elige con validacion cruzada sobre train, nunca mirando el test
print('\n2. BARRIDO DE K')
ks = [1, 3, 5, 7, 9, 11, 13, 15]
accs = []
for k in ks:
    pipe = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=k))
    cv = cross_val_score(pipe, X_train, y_train, cv=5)
    accs.append(cv.mean())
    print(f'k={k:>2}: accuracy CV={cv.mean():.4f}')

mejor_k = ks[int(np.argmax(accs))]
print(f'\nel k elegido es {mejor_k} (accuracy CV {max(accs):.4f})')

plt.figure(figsize=(8,5))
plt.plot(ks, accs, marker='o', color='tab:blue')
plt.title('Accuracy de validacion cruzada contra k')
plt.xlabel('k')
plt.ylabel('accuracy CV en train')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(CARPETA_IMG / 'knn_barrido_k.png')
plt.close()
print('knn_barrido_k.png guardado')


# 3. MODELO FINAL Y EVALUACION (el test se toca UNA sola vez, aqui)
print('\n3. MODELO FINAL')
# el scaler se ajusta SOLO con train, para no espiar el test
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

modelo = KNeighborsClassifier(n_neighbors=mejor_k)
modelo.fit(X_train_s, y_train)
pred = modelo.predict(X_test_s)   # unica vez que se mira el test, y ya sin decidir nada con el
acc = accuracy_score(y_test, pred)

# la clase mayoritaria
mayor = y_train.value_counts().idxmax()
base = (y_test == mayor).mean()
print(f'accuracy del modelo: {acc:.4f}')
print(f'accuracy del modelo base (siempre decir {mayor}): {base:.4f}')
print(f'el KNN le gana al piso por {(acc - base) * 100:.1f} puntos')

print('\nmatriz de confusion (filas = real, columnas = predicho):')
clases = sorted(y.unique())
cm = confusion_matrix(y_test, pred, labels=clases)
print(pd.DataFrame(cm, index=clases, columns=clases))

print('\nreporte por clase:')
print(classification_report(y_test, pred))


# 4 DISPERSION COLOREADA POR CLASE 
print('\n4. DISPERSION POR CLASE')
# los mismos colores
colores_pais = {'EEUU': 'tab:blue', 'MEXICO': 'tab:green', 'GUATEMALA': 'tab:orange'}
plt.figure(figsize=(9,6))
for pais in sorted(df['pais'].unique()):
    parte = df[df['pais'] == pais]
    plt.scatter(parte['mag'], parte['depth'], s=8, alpha=0.4,
                label=pais, color=colores_pais[pais])
plt.title('Sismos en el espacio mag-depth, coloreados por pais')
plt.xlabel('mag')
plt.ylabel('depth')
plt.legend()
plt.tight_layout()
plt.savefig(CARPETA_IMG / 'knn_clases_mag_depth.png')
plt.close()
print('knn_clases_mag_depth.png guardado')
print('aqui se ve por que el modelo puede acertar, Guatemala vive en otra zona (la profunda)')


# 5 KNN A MANO COMO VERIFICACION 
print('\n5. KNN A MANO VS SKLEARN')

def euclidean_distance(p_1, p_2):
    return np.sqrt(np.sum((p_2 - p_1) ** 2))

def k_nearest_neighbors(points, labels, input_data, k):
    # distancias, argsort, y votacion por mayoria
    predicciones = []
    for input_point in input_data:
        dists = [euclidean_distance(input_point, point) for point in points]
        vecinos = np.argsort(dists)[:k]
        votos = Counter(labels[i] for i in vecinos)
        predicciones.append(votos.most_common(1)[0][0])
    return predicciones

# a mano y con ciclos tardaria minutos con los aprox 2368 del test, asi que la verificacion
# se hace sobre una muestra de 200, si la logica esta bien, debe coincidir casi todo
rng = np.random.default_rng(42)
idx = rng.choice(len(X_test_s), size=200, replace=False)
muestra_X = X_test_s[idx]
muestra_y = y_test.iloc[idx].values

pred_man = k_nearest_neighbors(X_train_s, y_train.values, muestra_X, mejor_k)
pred_sk = modelo.predict(muestra_X)
coincidencia = np.mean(np.array(pred_man) == pred_sk)
acc_man = np.mean(np.array(pred_man) == muestra_y)
print(f'coincidencia KNN a mano vs sklearn (200 puntos): {coincidencia * 100:.1f}%')
print(f'accuracy del KNN a mano en esa muestra: {acc_man:.4f}')




print('\n--------RESUMEN--------')
print('Idea: clasificar el pais de un sismo por como se registro, sin lat/lon')
print(f'k elegido por CV en train: {mejor_k} | accuracy final en test: {acc:.4f} | piso mayoritario: {base:.4f}')
print(f'en CV, sin escalar {acc_sin:.4f} y con escalado {acc_con:.4f}: escalar si importa')
print('el test solo se uso una vez, al final, y ya sin decidir nada con el')
print('para el por que de cada cosa, ver Justificacion6.md')