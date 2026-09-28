# Practica 5 Modelos lineales y correlacion

# correlacion entre variables numericas y dos modelos lineales con su R2
# modelo 1 conteo de sismos por mes contra indice de tiempo 
# modelo 2 el par de variables que la matriz de correlacion diga que esta mas fuerte

# NOTA: lo de volver la fecha un indice 0,1,2 etc. y lo de graficar dispersion con linea roja
# viene "inspirado" de linear_regression.org del material de la materia, pero aqui los coeficientes se sacan con model.params

import pandas as pd
import numpy as np
import numbers
from pathlib import Path
import matplotlib
matplotlib.use('Agg')   #  para que no abra ventanas

import matplotlib.pyplot as plt
import statsmodels.api as sm

try:
    CARPETA = Path(__file__).parent
except NameError:
    CARPETA = Path.cwd()

RUTA_LIMPIO = CARPETA / 'Earthquake_limpio.csv'
CARPETA_IMG = CARPETA / 'Graficas'
CARPETA_IMG.mkdir(exist_ok=True)

df = pd.read_csv(RUTA_LIMPIO, parse_dates=['time'])

# otra vez la funcion de formato de la practica 4
def formato_p(p):
    if pd.isna(p):
        return '-'
    if p == 0:
        return '<1x10^-300'
    if p < 0.0001:
        texto = f'{p:.2e}'
        mantisa, expo = texto.split('e')
        return f'{mantisa}x10^{int(expo)}'
    return f'{p:.4f}'


NUMERICAS = ['mag', 'depth', 'nst', 'gap', 'dmin', 'rms', 'magNst']

# 1 CORRELACION, pearson y spearman, y de ahi sale el par del modelo 2
print('\n1. MATRIZ DE CORRELACION')
pearson = df[NUMERICAS].corr()
spearman = df[NUMERICAS].corr(method='spearman')   # spearman manda para elegir porque ya sabemos que no hay normalidad
print('pearson:')
print(pearson.round(3))
print('\nspearman:')
print(spearman.round(3))

# todos los pares posibles con su correlacion, ordenados por fuerza
pares = []
for i, a in enumerate(NUMERICAS):
    for b in NUMERICAS[i+1:]:
        pares.append((a, b, spearman.loc[a, b]))
pares.sort(key=lambda t: abs(t[2]), reverse=True)

print('\ntop 5 de pares segun |spearman| (valor absoluto):')
for a, b, v in pares[:5]:
    print(f'{a} vs {b}: rho={v:.3f} (pearson r={pearson.loc[a, b]:.3f})')

mejor_par = (pares[0][0], pares[0][1])
rho = pares[0][2]
r_pear = pearson.loc[mejor_par[0], mejor_par[1]]
print(f'\nel par elegido para el modelo 2: {mejor_par[0]} vs {mejor_par[1]} (rho={rho:.3f})')

# revisiones que revisamos antes de confiar en el par ganador
if 'depth' in mejor_par:
    print('OJO: el par ganador lleva depth, las profundidades por defecto del USGS')
    print('(profundidad_estimada=True) pueden estar inflando esta correlacion')
if abs(r_pear - rho) > 0.15:
    print('OJO: pearson y spearman no coinciden mucho en este par,')
    print('puede que la relacion no sea tan lineal, la dispersion lo va a mostrar')


# funcion para ajustar y graficar un modelo lineal
def modelo_lineal(x_num, y_num, titulo, xlabel, ylabel, nombre_png, marcas_x=None):
    X = sm.add_constant(x_num)
    modelo = sm.OLS(y_num, X).fit()
    print(f'\n{titulo}')
    print(f'R2 = {modelo.rsquared:.4f} | R2 ajustada = {modelo.rsquared_adj:.4f}')
    b0, b1 = modelo.params
    print(f'ecuacion: y = {b0:.4f} + {b1:.4f} * x')
    print(f'p de la pendiente: {formato_p(modelo.pvalues.iloc[1])}')

    plt.figure(figsize=(9,6))
    plt.scatter(x_num, y_num, s=10, alpha=0.5, color='tab:blue')
    plt.plot(x_num, b0 + b1 * x_num, color='red', label='regresion')
    # la verde siempre predice el promedio 
    # si la roja queda casi pegada a la verde, la recta no aporta nada
    plt.plot(x_num, [y_num.mean()] * len(x_num), color='green', label='promedio de y (modelo base)')
    if marcas_x is not None:
        plt.xticks(marcas_x[0], marcas_x[1], rotation=90)
    plt.title(titulo)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.tight_layout()
    plt.savefig(CARPETA_IMG / nombre_png)
    plt.close()
    print(f'{nombre_png} guardado')
    return modelo


# MODELO 1 conteo de sismos por mes contra indice de tiempo
print('\nMODELO 1: sismos por mes vs tiempo')
por_mes = df.groupby(df['time'].dt.to_period('M')).size().reset_index(name='conteo')
# como el mes es texto/fecha, se vuelve un indice 0,1,2 para poder regresar
por_mes['indice'] = range(len(por_mes))
meses_str = [str(m) for m in por_mes['time']]
marcas = (list(range(0, len(por_mes), 12)), meses_str[::12])

m1 = modelo_lineal(por_mes['indice'], por_mes['conteo'],
                   'Sismos por mes contra indice de tiempo',
                   'mes', 'cuantos sismos', 'lr_sismos_mes.png', marcas_x=marcas)

if m1.rsquared < 0.05:
    print('la roja queda casi pegada a la verde: no hay tendencia lineal clara,')
    print('el conteo mensual no crece ni decrece con el tiempo')
else:
    print('si se alcanza a ver algo de tendencia lineal en el conteo mensual')




# MODELO 2: el par que eligio la matriz de correlacion
print('\nMODELO 2: el par mas correlacionado')
a, b = mejor_par
m2 = modelo_lineal(df[a], df[b], f'{b} contra {a}', a, b, f'lr_{b}_{a}.png')
print(f'la recta explica un {m2.rsquared*100:.1f}% de la variabilidad de {b} usando {a}')





print('\nRESUMEN')
print(f'modelo 1 (conteo mensual vs tiempo): R2 = {m1.rsquared:.4f}')
print(f'modelo 2 ({b} vs {a}): R2 = {m2.rsquared:.4f}')
print('el R2 es el porcentaje de variabilidad que la recta alcanza a explicar;')
print('cerca de 0 quiere decir que la recta no aporta nada sobre decir nomas el promedio')
print('para el por que de cada cosa, ver Justificacion5.md')