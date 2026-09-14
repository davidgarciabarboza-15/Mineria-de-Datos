# Practica 4: Pruebas Estadisticas

# NOTA: la idea de ajustar ols con formula y usar anova_lm viene del data_analysis.org
# pero aqui lo aplicamos a los sismos 
# (shapiro-wilk, levene y el post-hoc)
# se requiere: pip install scipy statsmodels

import pandas as pd
import numpy as np
from pathlib import Path
from itertools import combinations
from scipy import stats
import statsmodels.api as sm
from statsmodels.formula.api import ols

try:
    CARPETA = Path(__file__).parent
except NameError:
    CARPETA = Path.cwd()

RUTA_LIMPIO = CARPETA / 'Earthquake_limpio.csv'

df = pd.read_csv(RUTA_LIMPIO, parse_dates=['time'])

# tercera practica seguida reutilizando esta funcion, usandola al maximo
def categorize_pais(place: str) -> str:
    if 'Guatemala' in place: return 'GUATEMALA'
    if 'Honduras' in place: return 'HONDURAS'
    if 'Revilla Gigedo' in place or 'Gulf of California' in place: return 'MEXICO'
    if place.endswith('Mexico') and 'New Mexico' not in place: return 'MEXICO'
    if 'B.C.' in place or ', MX' in place: return 'MEXICO'
    return 'EEUU'

df['pais'] = df['place'].apply(categorize_pais)

ALPHA = 0.05   # el de siempre, 5%
GRUPOS = ['EEUU', 'MEXICO', 'GUATEMALA', 'HONDURAS']


# si el p es tan chico que python lo redondea a cero exacto, ya no sacamos
# el 0.00x10^0 (eso era lo que se mostraba), mejor <1x10^-300, que se entiende mas
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


def pedazos(variable):
    # separa los valores de la variable en una lista por pais
    return [df[df['pais'] == g][variable].values for g in GRUPOS]


def revisar_supuestos(grupos, variable):
    print(f'\nsupuestos para {variable}')
    print('revisamos si los datos son normales y si las varianzas se parecen,')
    print('porque de eso depende cual prueba creerle mas')
    # shapiro no funciona bien si le metes mas de 5000 datos de golpe, asi que
    # sacamos una muestra de 500 por grupo con semilla fija para que salga igual siempre
    rng = np.random.default_rng(42)
    for g, nombre in zip(grupos, GRUPOS):
        muestra = rng.choice(g, size=min(500, len(g)), replace=False)
        p = stats.shapiro(muestra).pvalue
        veredicto = 'normal' if p > ALPHA else 'no normal'
        print(f'shapiro {nombre}: p = {formato_p(p)} -> {veredicto}')
    p_levene = stats.levene(*grupos).pvalue
    veredicto = 'varianzas parecidas' if p_levene > ALPHA else 'varianzas distintas'
    print(f'levene: p = {formato_p(p_levene)} -> {veredicto}')


def post_hoc(grupos, variable, modo):
    # comparaciones por pares con bonferroni (multiplicamos p por el numero de pares)
    print(f'\npost-hoc por pares ({variable}, {modo}, bonferroni)')
    print('bonferroni multiplica el p por el numero de comparaciones, para no emocionarnos de mas')
    pares = list(combinations(range(len(GRUPOS)), 2))
    for i, j in pares:
        if modo == 't':
            # welch (equal_var=False) porque levene ya nos dijo que las varianzas no son parecidas
            p = stats.ttest_ind(grupos[i], grupos[j], equal_var=False).pvalue
        else:
            p = stats.mannwhitneyu(grupos[i], grupos[j], alternative='two-sided').pvalue
        p_adj = min(p * len(pares), 1.0)
        signo = 'difieren' if p_adj < ALPHA else 'no difieren'
        print(f'{GRUPOS[i]} vs {GRUPOS[j]}: p_adj = {formato_p(p_adj)} -> {signo}')


# COMPARACION 1: magnitud por pais (ruta ANOVA + t)
print('\nCOMPARACION 1: mag por pais')
grupos_mag = pedazos('mag')
revisar_supuestos(grupos_mag, 'mag')
print('nota: <1x10^-300 quiere decir que el p es tan chico que python lo redondea a cero')

#ols con formula y anova_lm tipo 2
modelo = ols('mag ~ C(pais)', data=df).fit()
tabla_anova = sm.stats.anova_lm(modelo, typ=2)
p_anova = tabla_anova['PR(>F)'].iloc[0]
print('\nANOVA (ols + anova_lm)')
print('de la tabla, la columna que importa es PR(>F), ese es el p del anova')
print('C(pais) = la variacion ENTRE paises, Residual = el ruido DENTRO de cada pais,')
print('si el p de C(pais) sale chico, es que los paises no son iguales')
print(tabla_anova.to_string(formatters={'PR(>F)': formato_p}))
if p_anova < ALPHA:
    print(f'p = {formato_p(p_anova)} < {ALPHA} -> si hay diferencias de magnitud entre paises')
else:
    print(f'p = {formato_p(p_anova)} >= {ALPHA} -> no se ven diferencias')

post_hoc(grupos_mag, 'mag', 't')

# cross-check, aunque los supuestos fallen, kruskal deberia llegar a lo mismo
h_kw, p_kw = stats.kruskal(*grupos_mag)
print(f'\ncross-check kruskal en mag: p = {formato_p(p_kw)}')

print('\nmedianas de mag por pais (para ver si la diferencia es relevante, no solo significativa):')
print(df.groupby('pais')['mag'].median())


# COMPARACION 2: profundidad por pais (ruta Kruskal-Wallis)
print('\nCOMPARACION 2: depth por pais')
grupos_depth = pedazos('depth')
revisar_supuestos(grupos_depth, 'depth')

# depth es aun menos normal que mag, asi que aqui la prueba principal es kruskal
h_kw2, p_kw2 = stats.kruskal(*grupos_depth)
print('\nKruskal-Wallis (la confiable cuando no hay normalidad)')
print(f'H={h_kw2:.3f}  p = {formato_p(p_kw2)}')
if p_kw2 < ALPHA:
    print(f'p = {formato_p(p_kw2)} < {ALPHA} -> si hay diferencias de profundidad entre paises')
else:
    print(f'p = {formato_p(p_kw2)} >= {ALPHA} -> no se ven diferencias')

post_hoc(grupos_depth, 'depth', 'mw')

# cross-check con anova de scipy, para ver que ambas rutas coinciden
f_stat, p_f = stats.f_oneway(*grupos_depth)
print(f'\ncross-check anova (f_oneway) en depth: p = {formato_p(p_f)}')

print('\nmedianas de depth por pais:')
print(df.groupby('pais')['depth'].median())






print('\n##### RESUMEN #####')
print('prueba            p-value')
print(f'anova mag         {formato_p(p_anova)}')
print(f'kruskal mag       {formato_p(p_kw)}')
print(f'kruskal depth     {formato_p(p_kw2)}')
print(f'anova depth       {formato_p(p_f)}')
print()
print('Conclusion: las cuatro pruebas coinciden en que si hay')
print('diferencias de magnitud y de profundidad entre paises, y esto no es casualidad')
print('como los datos no son normales, la prueba en la que nos apoyamos es')
print('kruskal-wallis, anova se quedo como comprobacion, y con tantos datos')
print('alcanza a ver lo mismo')
print('\npara el por que de cada bloque y cada numero, ver Justificacion4.md\n')


# NOTA: Algunos de estos temas los vimos en la materia de "Teoria de la informacion aplicada"
# Asi que nuevamente se tuvo que recordar conceptos importantes