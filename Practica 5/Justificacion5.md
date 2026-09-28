# Práctica 5 Modelos Lineales y Correlación 

El script de esta practica es `Modelos_Lineales.py`, los valores exactos (matrices de correlación, top de pares, R2 y p de cada modelo) quedan en las capturas de ejecución, y las dos gráficas se guardan en `Graficas` como `lr_dmin_gap.png` y `lr_sismos_mes.png`. 


Lo primero fue ver cuáles variables numéricas se correlacionan, y después ajustar dos modelos lineales con su gráfica y su R2.

## Elección del par del segundo modelo

En vez de escoger un par, se sacó la matriz de correlación de Pearson y de Spearman sobre las variables numéricas (mag, depth, nst, gap, dmin, rms, magNst), y se dejó que ganara el par con correlación más fuerte en valor absoluto de Spearman. Spearman manda para elegir porque desde la práctica 4 sabemos que los datos no son normales, y Spearman no asume normalidad ni línea recta, solo que la relación vaya siempre en el mismo sentido, que al subir una, la otra también suba (o ambas bajen), sin importar si es una recta perfecta o una curva. 


El par ganador fue gap contra dmin, y el script imprime un top 5 de pares para que la elección se aprecie.

En cuanto a la correlación de esas dos, las dos describen qué tan bien la red "vio" el sismo, dmin es la distancia a la estación más cercana que lo registró, y gap es el hueco azimutal más grande que queda entre las estaciones que reportaron (azimutal viene de azimut, o sea, dirección, visto desde el epicentro, cada estación que reporta queda en una dirección, y el gap es el hueco de dirección más grande que se queda sin estaciones). Si un sismo ocurre lejos de cualquier estación, la cobertura es pobre y el gap crece, por eso la relación positiva. 

El código hace además dos revisiones antes de confiar en el par, avisa si el ganador involucra depth (las profundidades por defecto del USGS podrían inflar la correlación) y avisa si Pearson y Spearman discrepan mucho (señal de que la relación no es lineal). En esta corrida el ganador no lleva depth, así que la primera revisión no tuvo que activarse.

## Modelo 1 conteo mensual contra tiempo

Se "imita" el ejemplo de la materia, se agrupa por mes, se cuentan los sismos, y como el mes no es numérico se convierte en un índice 0, 1, 2, etc, para poder regresionarlo. Después un OLS con statsmodels y la gráfica con la dispersión, la recta roja de la regresión y la línea verde del promedio de y.

Lo que se ve en la gráfica es justo lo que ya se intuia desde la práctica 3, la recta roja queda casi plana y pegada a la verde. Hay meses con enjambres (los picos de alrededor de 250 sismos) y meses tranquilos, pero alrededor de un piso de unos 100 sismos que no crece ni decrece con los años. 


La conclusión es que no hay tendencia lineal, el conteo mensual no va subiendo ni bajando ordenadamente, y el R2 salió casi cero. La regresión aquí no le gana a la línea verde, predecir siempre el promedio da básicamente lo mismo.

## Modelo 2 dmin contra gap azimutal, el par de la matriz

La gráfica de este modelo se ve distinta, con gap chico, dmin está casi obligado a ser chico (buena cobertura implica una estación cerca), y con gap grande, dmin puede ser casi cualquier cosa aunque en promedio crece. La recta roja con pendiente positiva se separa claramente de la verde, así que sí, hay una tendencia que la recta captura, pero la dispersión es enorme, el R2 queda moderado, no alto. La forma de la grafica explica que la relación es más de tendencia monotónica que de línea apretada, y por eso se eligió con Spearman.




## La línea verde y contra qué compara el R2

La línea verde es el modelo base o modelo nulo, es decir, el que siempre predice el promedio de y sin mirar x. R2 se define comparando contra ese modelo, R2 = 1 menos (el error de la recta) entre (el error del promedio). Por eso, en el modelo 1, donde la roja queda pegada a la verde, el R2 es casi cero, y en el modelo 2, donde se separan, el R2 si sube. 

## Lo que podemos deducir de los 2 modelos

Por un lado, la actividad sísmica no tiene una tendencia a subir o bajar con el tiempo, se mantiene más o menos igual (aunque con sus picos por réplicas), tal como ya habíamos visto en las prácticas 3 y 4. Por otro lado, las métricas de cobertura (gap y dmin) sí se relacionan, pero los datos están muy dispersos, así que una línea recta no alcanza a explicarlos del todo.

## NOTAS

1. El script está inspirado en el ejemplo de linear_regression.org del material de la materia.
2. El par del modelo 2 lo eligió la matriz de correlación en la ejecución, no se fijó a mano, el top 5 impreso y las matrices quedan en las capturas.
3. Referencias consultadas:
   - https://github.com/ppGodel/data_mining (material de la materia; ejemplo de regresión lineal con datos de UANL)
   - https://en.wikipedia.org/wiki/Coefficient_of_determination (contra qué compara exactamente el R2 y por qué la línea del promedio es la base)
   - https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.OLS.html (OLS de statsmodels)
   - https://en.wikipedia.org/wiki/Spearman%27s_rank_correlation_coefficient (concepto para Pearson/Spearman)
