# Práctica 8 Pronóstico (Forecasting)

Se armó un modelo para pronosticar los meses futuros de una serie y evaluar qué tan bien lo hace, la serie elegida es el conteo mensual de sismos, la misma que venimos siguiendo desde la práctica 3, con 80 meses que van de 2020-01 a 2026-08 (hasta la fecha en el que se descargó el dataset).

## La partición por tiempo y los cuatro contendiente

Aquí la partición no puede ser al azar como en la práctica 6, porque si el entrenamiento ve meses futuros el error sale mintiendo. 


Se entrenó con los primeros 68 meses y se reservaron los últimos 12 como holdout, que es donde se mide a todos por igual. Los cuatro contendientes son una regresión sobre el índice de tiempo, el promedio del entrenamiento como modelo base, el pronóstico naive que repite el último valor visto, y Holt, un suavizamiento exponencial con tendencia de statsmodels.

En el holdout los errores quedaron así, la regresión con MAE 35.23 y RMSE 42.38, el promedio con 34.23 y 41.76, el naive con 26.00 y 43.67, y Holt con 29.71 y 40.04. El MAE es el error típico de un mes cualquiera y el RMSE castiga más los errores grandes.

## Por qué las métricas no se ponen de acuerdo

El naive ganó el MAE con margen pero tuvo el peor RMSE de los cuatro, y eso no suena muy bien que digamos. El holdout resultó ser un tramo de actividad baja respecto al promedio histórico, así que repetir el último valor del entrenamiento, que ya estaba en ese nivel bajo, acertó bien los meses tranquilos y por eso su error típico es el menor, pero cuando el holdout tuvo meses con enjambre, el naive se equivocó más feo que nadie, y eso es justo lo que el RMSE castiga y el MAE perdona. Los modelos de nivel, o sea promedio, regresión y Holt, se equivocan más parejo y por eso pierden el MAE pero ganan el RMSE.

Elegir al ganador depende entonces de qué error me importe, si me importa el error típico de un mes cualquiera, el naive, pero si me importa no llevarme un susto grande en un mes de enjambre, Holt. El script eligió por MAE y por eso el naive pasó al siguiente paso, y esa decisión queda documentada aquí con sus dos caras en vez de esconder la discusión.

## El pronóstico de los siguientes seis meses

Reajustando el naive con la serie completa, el pronóstico de los siguientes seis meses es de 33 sismos por mes, que es simplemente el valor del último mes del catálogo, con una banda de menos 69 a 135 sismos. Dos cosas se leen de ahí: la primera es que el ancla del naive es un solo mes, y ese último mes de 33 sismos es de los más bajos de toda la serie, así que el pronóstico hereda ese ruido y es frágil por construcción. La segunda es que la banda pisa valores negativos, que son imposibles para un conteo, y eso no es un error del código sino la señal de que el ruido de esta serie no es simétrico, porque los enjambres la cargan hacia arriba, y una banda simétrica de más o menos desviaciones le queda chica de un lado y larga del otro.

La gráfica forecast_holdout.png deja ver lo mismo en el holdout, con la banda del naive hundida por debajo de cero y el pico de casi 200 sismos de mediados de 2026 muy por encima de ella, mientras la recta roja plana en unos 70 sismos atraviesa los meses tranquilos sin perseguir ni los picos ni los valles.

## Conclusión

Con esta serie el pronóstico honesto es un nivel con incertidumbre ancha y nada más, la regresión no le gana al promedio porque no hay tendencia que explotar, como ya se había visto en la práctica 5, y el naive que ganó el MAE lo hizo por el régimen de actividad baja del holdout y no por una virtud del método, con el detalle de que su ancla de 33 sismos viene de uno de los meses más bajos del catálogo y su banda pisa negativos. Si hubiera que quedarse con un pronóstico operativo, Holt es el que balancea error típico y error peor caso, con MAE 29.71 y el mejor RMSE de los cuatro, y el naive es justo el ejemplo de que el mejor número en una métrica no siempre viene del mejor modelo.

## Notas

1. Del forecasting.org del material se toma la idea de volver el mes un índice numérico, la idea de pronosticar extrapolando la recta ajustada en el tiempo y el fill_between como banda en la gráfica.
2. La banda del pronóstico se armó con los residuales del modelo en el entrenamiento y no con las bandas de coeficientes del material, que no son un intervalo para meses nuevos.
3. Referencias consultadas
   - https://github.com/ppGodel/data_mining (material de la materia, forecasting.org con la regresión sobre tiempo y las bandas)
   - https://en.wikipedia.org/wiki/Exponential_smoothing (suavizamiento exponencial y Holt)
   - https://en.wikipedia.org/wiki/Mean_absolute_error (qué mide el MAE y cómo se lee)
   - https://en.wikipedia.org/wiki/Root-mean-square_deviation (qué mide el RMSE y por qué castiga los errores grandes)
