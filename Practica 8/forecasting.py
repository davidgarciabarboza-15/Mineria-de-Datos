# Practica 8 Pronostico (Forecasting)
# serie mensual de conteo de sismos y pronostico de meses futuros
# cuatro contendientes: regresion sobre indice de tiempo,
# promedio del train (el modelo base), naive (repetir el ultimo valor)
# y Holt (suavizamiento exponencial con tendencia) de statsmodels
# la evaluacion es en los ultimos 12 meses, particion por tiempo, no al azar,
# porque si el train ve meses futuros el error sale mentiroso

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.holtwinters import ExponentialSmoothing

try:
    CARPETA = Path(__file__).parent
except NameError:
    CARPETA = Path.cwd()

RUTA_LIMPIO = CARPETA / 'Earthquake_limpio.csv'
CARPETA_IMG = CARPETA / 'Grafica'  
CARPETA_IMG.mkdir(exist_ok=True)

df = pd.read_csv(RUTA_LIMPIO, parse_dates=['time'])


# la serie, conteo de sismos por mes, la misma que venimos usando desde la practica 3
por_mes = df.groupby(df['time'].dt.to_period('M')).size().reset_index(name='conteo')
por_mes['indice'] = range(len(por_mes))   # el mes se vuelve 0,1,2...
print(f'\nmeses en la serie: {len(por_mes)} (de {por_mes["time"].iloc[0]} a {por_mes["time"].iloc[-1]})')


# 1 PARTICION TEMPORAL train = todo menos los ultimos 12 meses
HOLDOUT = 12
train = por_mes.iloc[:-HOLDOUT].copy()
test = por_mes.iloc[-HOLDOUT:].copy()
y_train = train['conteo'].values
y_test = test['conteo'].values

print('\n1. PARTICION TEMPORAL')
print(f'train: {len(train)} meses | holdout: {len(test)} meses (los mas recientes)')




print('\n2. CONTENDIENTES EN EL HOLDOUT')

# (a) regresion sobre indice de tiempo: ajusta en train y extrapola
X_train = sm.add_constant(train['indice'])
modelo_lr = sm.OLS(train['conteo'], X_train).fit()
X_test = sm.add_constant(test['indice'])   # el indice sigue corriendo, asi que extrapolar es natural
pred_lr = np.asarray(modelo_lr.predict(X_test))
resid_lr = y_train - np.asarray(modelo_lr.predict(X_train))

# (b) promedio del train: el modelo base, el que no ve tendencia ni nada
pred_mean = np.full(HOLDOUT, train['conteo'].mean())
resid_mean = y_train - train['conteo'].mean()

# (c) naive: repetir el ultimo valor visto en train
pred_naive = np.full(HOLDOUT, train['conteo'].iloc[-1])
resid_naive = y_train[1:] - y_train[:-1]   # su error de un paso dentro del train

# (d) Holt: suavizamiento exponencial con tendencia, ajustado solo con train
holt = ExponentialSmoothing(train['conteo'], trend='add', seasonal=None, initialization_method='estimated').fit()
pred_holt = np.asarray(holt.forecast(HOLDOUT))
resid_holt = np.asarray(holt.resid)

preds = {
    'regresion tiempo': pred_lr,
    'promedio train': pred_mean,
    'naive ultimo valor': pred_naive,
    'holt': pred_holt,
}
resids = {
    'regresion tiempo': resid_lr,
    'promedio train': resid_mean,
    'naive ultimo valor': resid_naive,
    'holt': resid_holt,
}

# como la practica 5 ya mostro que esta serie no tiene tendencia, no es raro si regresion
# y promedio quedan casi empatados, aqui el nivel es casi todo lo que hay
print(f'{"modelo":<20}{"mae":>8}{"rmse":>8}')
maes = {}
for nombre, p in preds.items():
    mae = np.mean(np.abs(y_test - p))
    rmse = np.sqrt(np.mean((y_test - p) ** 2))
    maes[nombre] = mae
    print(f'{nombre:<20}{mae:>8.2f}{rmse:>8.2f}')

ganador = min(maes, key=maes.get)
print(f'\nel que menos error tuvo en el holdout: {ganador} (mae {maes[ganador]:.2f})')

# banda de incertidumbre del ganador, su pronostico mas/menos 1.96 desviaciones de sus
# residuales en train, o sea donde deberia caer un mes nuevo aprox 95% de las veces si el ruido se repite
sd_res = np.std(resids[ganador], ddof=1)

t_test = test['time'].dt.to_timestamp()
plt.figure(figsize=(11,6))
plt.plot(por_mes['time'].dt.to_timestamp(), por_mes['conteo'], marker='.', linestyle='-', color='tab:blue', label='serie real')
plt.axvline(t_test.iloc[0], color='gray', linestyle='--', label='particion train / holdout')
plt.plot(t_test, preds[ganador], marker='o', color='red', label=f'pronostico {ganador}')
plt.fill_between(t_test, preds[ganador] - 1.96 * sd_res, preds[ganador] + 1.96 * sd_res, alpha=0.2, color='orange', label='banda aprox 95%')
plt.xticks(rotation=90)
plt.title('Conteo mensual de sismos: holdout y pronostico')
plt.ylabel('cuantos sismos')
plt.legend()
plt.tight_layout()
plt.savefig(CARPETA_IMG / 'forecast_holdout.png')
plt.close()
print('forecast_holdout.png guardado')


# PRONOSTICO DE LOS SIGUIENTES 6 MESES (futuro real, refit con toda la serie)
FUT = 6
print(f'\n3. PRONOSTICO DE LOS SIGUIENTES {FUT} MESES')
print(f'se reajusta {ganador} con toda la serie, porque ya no hay nada que reservar')

if ganador == 'regresion tiempo':
    X_all = sm.add_constant(por_mes['indice'])
    m_all = sm.OLS(por_mes['conteo'], X_all).fit()
    idx_fut = np.arange(len(por_mes), len(por_mes) + FUT)
    pred_fut = np.asarray(m_all.predict(sm.add_constant(idx_fut)))
    sd_fut = np.std(m_all.resid, ddof=1)
elif ganador == 'promedio train':
    media_all = por_mes['conteo'].mean()
    pred_fut = np.full(FUT, media_all)
    sd_fut = np.std(por_mes['conteo'] - media_all, ddof=1)
elif ganador == 'naive ultimo valor':
    pred_fut = np.full(FUT, por_mes['conteo'].iloc[-1])
    sd_fut = np.std(np.diff(por_mes['conteo']), ddof=1)
else:   # holt
    holt_all = ExponentialSmoothing(por_mes['conteo'], trend='add', seasonal=None, initialization_method='estimated').fit()
    pred_fut = np.asarray(holt_all.forecast(FUT))
    sd_fut = np.std(holt_all.resid, ddof=1)

ult = por_mes['time'].iloc[-1]
fut_meses = [ult + i for i in range(1, FUT + 1)]
for m, v in zip(fut_meses, pred_fut):
    print(f'{m}: {v:.1f} sismos (banda aprox 95% de {v - 1.96 * sd_fut:.1f} a {v + 1.96 * sd_fut:.1f})')



print('\nLo que se vio: ')
print(f'se trabajo con el conteo mensual de sismos a lo largo de {len(por_mes)} meses,')
print(f'reservando los ultimos {HOLDOUT} como holdout, donde el que menos se equivoco')
print(f'fue {ganador} con un mae de {maes[ganador]:.2f}.')
print(f'con el modelo reajustado en toda la serie salieron los {FUT} meses de pronostico con su banda,')
print('y la idea que queda es que en una serie sin tendencia y con enjambres')
print('el pronostico honesto es el nivel con banda ancha')
print('\nPara mas detalle ver Justificacion8.md\n')