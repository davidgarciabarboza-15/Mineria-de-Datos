# Práctica 4 Pruebas Estadísticas

El script de esta práctica es `Pruebas_Estadisticas.py` y su salida completa está en las capturas del repositorio. 


La idea general era comprobar si la magnitud y la profundidad de los sismos realmente cambian de un país a otro, o si las diferencias que vimos en las prácticas anteriores podían ser solo cosa del azar de la muestra. Al final de su salida, el script imprime un resumen.

## Qué se comprobó y con qué

La indicación pide comprobar diferencias en datos etiquetados mediante ANOVA y prueba t, o con Kruskal-Wallis, como etiqueta usamos el país (la categoría `pais` que venimos explotando desde la práctica 2), con cuatro grupos: EEUU, MEXICO, GUATEMALA y HONDURAS. 


Se hicieron 2 comparaciones: magnitud por país y profundidad por país. En la primera se siguió la ruta de ANOVA con pruebas t como post-hoc, en la segunda, la ruta de Kruskal-Wallis con Mann-Whitney, y en las dos se corrió también la prueba de la otra ruta como comprobación, para ver si coincidían.

La hipótesis nula (H0) dice que todos los países son iguales en esa variable y que cualquier diferencia que veamos es ruido, la alternativa dice que al menos un país es distinto. El p-value es la probabilidad de ver diferencias tan grandes como las nuestras si H0 fuera cierta, y se compara contra 0.05, si queda por debajo, H0 se rechaza.

## Por qué se revisaron supuestos

ANOVA supone datos normales y varianzas parecidas, y si eso no se cumple su p-value no es del todo confiable, Kruskal-Wallis no supone nada de eso, entonces, para saber a cuál de las dos rutas creerle, había que mirar primero los datos: Shapiro-Wilk para normalidad y Levene para varianzas. 

Un pequeño detalle es que Shapiro no acepta más de 5000 datos de golpe y el grupo de EEUU tiene 5071, así que se sacó una muestra de 500 por grupo con semilla fija (42) para que el resultado salga igual en cada ejecución.

En las dos variables todo salió no normal y con varianzas distintas, por eso la prueba en la que nos apoyamos es Kruskal-Wallis y ANOVA queda como comprobación.

## Comparación 1: magnitud por país

El ANOVA se hizo como en el material de la materia: se ajusta un modelo con fórmula (`mag ~ C(pais)`) y se saca la tabla tipo 2 con anova_lm de statsmodels. De esa tabla lo que importa es la columna PR(>F) de la fila C(pais), que es el p de la prueba, la fila C(pais) recoge la variación entre países y la fila residual la variación dentro de cada país. El p salió más chico de lo que python alcanza a escribir, así que se rechaza H0, entonces la magnitud no es igual entre países.

Para ver cuáles pares difieren se hicieron pruebas t por pares (Welch, porque Levene ya había dicho que las varianzas no son parecidas) con corrección de Bonferroni, que es simplemente multiplicar cada p por el número de comparaciones hechas (6), para no creer diferencias que aparecen nada mas por hacer muchas pruebas. Difieren todos los pares excepto GUATEMALA vs HONDURAS, cuyo p ajustado fue 1.0, esto tiene sentido ya que sus medianas son 4.30 y 4.40 con apenas 207 y 34 sismos, no hay evidencia para separarlos.

## Comparación 2: profundidad por país

Aquí la prueba principal fue Kruskal-Wallis directamente, porque la profundidad es aún menos normal que la magnitud. También dio p por debajo de 0.05, la profundidad sí cambia entre países. El post-hoc por pares fue con Mann-Whitney y el mismo Bonferroni. 


Algo que llamó la atención es que MEXICO y HONDURAS sí difieren (p ajustado 0.0145) aunque los dos tienen mediana de 10 km, esto es debido a que Mann-Whitney compara toda la distribución y no solo la mediana, y México tiene una cola más profunda.

## Por qué casi todo sale 0

Con casi 8000 sismos las pruebas tienen mucho peso, cualquier diferencia real, aunque sea chica, sale significativa, por eso los p salieron tan pequeños que python los redondea a 0. Al principio se imprimian con seis decimales y todo se veía como 0.000000, que no se entendía (parecía un error), así que se cambió el formato, si la p es menor a 0.0001 se imprime en notación científica (por ejemplo 1.99x10^-114), y si es tan chico que python lo ve como cero exacto se imprime <1x10^-300. Para saber si la diferencia importa en la práctica y no solo estadísticamente, al final de cada comparación se dejan las medianas por país: en magnitud, 2.77 en EEUU contra 4.2 o 4.3 en MEXICO y GUATEMALA, en profundidad, unos 7 km en EEUU contra 10 en MEXICO y HONDURAS, y unos 74 en GUATEMALA.

Y ¿por qué Kruskal es en la que nos apoyamos si todas "coinciden"? Porque de las pruebas globales es la única cuyo p es válido sin condiciones con la forma que tienen los datos (no normales y con varianzas distintas). ANOVA acertó gracias a que la muestra es enorme, pero con grupos chicos y no normales pudo haber fallado. Que las dos rutas lleguen al mismo lugar no las vuelve equivalentes.

## Principales referencias consultadas:
   - https://github.com/ppGodel/data_mining/blob/main/data_analysis.org (material de la materia, base del ANOVA con ols)
   - https://docs.scipy.org/doc/scipy/reference/stats.html (pruebas de scipy shapiro, levene, kruskal, mannwhitneyu)
   - https://www.statsmodels.org/stable/generated/statsmodels.stats.anova.anova_lm.html (anova_lm de statsmodels)
   - https://medium.com/@sabourinleandre/post-hoc-tests-explained-tukey-bonferroni-holm-bonferroni-and-scheff%C3%A9s-test-ed362b820842 (inoformación general de Bonferroni)
   - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html (prueba de Kruskal-Wallis)
   - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html (prueba de Mann-Whitney U, el post-hoc de la ruta de Kruskal)
   - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html (prueba t por pares, con equal_var=False es la t de Welch)
   - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.shapiro.html (Shapiro-Wilk)  
