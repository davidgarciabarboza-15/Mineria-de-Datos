# Práctica 6 Clasificación de Datos

El script de esta práctica es KNN.py. 

Los números exactos (accuracy de cada experimento, k elegido, matriz de confusión y reporte por clase) quedan en las capturas de ejecución, y las dos gráficas se guardan como knn_barrido_k.png y knn_clases_mag_depth.png. 


La idea fue clasificar de qué país es un sismo usando únicamente cómo se registró, con el algoritmo KNN.

## Qué se armó 

La etiqueta es el país (la que arrastramos desde la práctica 2), recortada a tres clases, EEUU, MEXICO y GUATEMALA. Honduras quedó fuera de la clasificación a propósito porque con apenas 34 sismos, en una partición estratificada 70/30 quedarían unos 24 ejemplos en entrenamiento y unos 10 en test, muy pocos para que el modelo aprenda la clase, excluirla evita reportar métricas sin significado para esa categoría.

Las características son cómo se registró el sismo, profundidad, magnitud, número de estaciones (nst y magNst), gap azimutal (el hueco de dirección más grande entre las estaciones que reportaron), distancia a la estación más cercana (dmin) y rms. 


Latitud y longitud se dejaron fuera a propósito, y aquí está el punto, porque con ellas, el país es puramente geografía (un sismo en Texas es de EEUU porque está en Texas), y el modelo acertaría casi todo sin aprender nada, entonces sin ellas, la pregunta que queda es: si la huella de cómo se registró el sismo alcanza para revelar el país.

Los datos se parten 70/30 en entrenamiento y prueba, de forma estratificada (cada parte conserva la misma proporción de clases que el total) y con semilla 42 para que la partición sea la misma en cada ejecución.

## KNN y por qué escalar

KNN clasifica por votación, para un sismo nuevo busca los k sismos ya conocidos más parecidos y deja que la clase mayoritaria entre esos vecinos decida, ese parecido, se calcula con la distancia entre los valores de las características (profundidad, magnitud, gap, etc.), y aquí está el detalle, si cada característica vive en una escala distinta, las más grandes dominan el cálculo. El gap va de 0 a 360 y el dmin de 0 a 8, así que con los valores crudos la distancia entre dos sismos dependería casi solo del gap y el resto de las características no pesaría, por eso, el mismo KNN se corrió con y sin StandardScaler, que deja cada característica con media 0 y varianza 1 para que todas pesen parejo, ambas versiones se compararon con validación cruzada sobre el entrenamiento y la escalada es la que gana (por cuánto, queda en las capturas). El scaler se ajusta solo con entrenamiento para no espiar el test.

## Cómo se eligió k y por qué el test no se toca hasta el final

El k se eligió barriendo valores (1, 3, 5, hasta 15) y evaluando cada candidato con validación cruzada de 5 folds sobre el entrenamiento nada más, el entrenamiento se parte 5 veces en 4 pedazos para ajustar y 1 para medir, y se promedian las 5 mediciones. La curva de accuracy contra k queda en knn_barrido_k.png y el valor elegido aparece en las capturas.  

La razón de no elegir k mirando el accuracy del test es que el test sirve para estimar cómo le va al modelo con datos que nunca vio durante el ajuste, si además se usa para tomar decisiones (como con qué k quedarnos), esa estimación deja de ser limpia porque el accuracy final sale más alto de lo que realmente sería con datos nuevos. Con validación cruzada, todas las decisiones (escalar, elegir k) se toman mirando solo el entrenamiento, y el test se evalúa una única vez, al final, con el modelo ya cerrado.

Junto al accuracy del modelo final se imprime el accuracy de un modelo base, uno que siempre predice la clase mayoritaria (EEUU) sin usar ninguna característica. Ese número es la referencia mínima, porque cualquier modelo que no lo supere no estaría aprendiendo nada, después, vienen la matriz de confusión (cuántos sismos de cada país quedaron bien o mal clasificados y con qué país se confundieron) y el reporte por clase (precisión y recall de cada país).

## Cómo se leen los resultados

Guatemala se clasifica casi sin error porque sus sismos viven en otra parte del espacio de características, profundidad mediana de unos 74 km contra unos 7 km de EEUU y unos 10 km de MEXICO, una diferencia que ya teníamos desde la práctica 4. 


EEUU y MEXICO en cambio se prestan a confusión porque ambos son sismos mayormente de poca profundidad y con coberturas parecidas, y sus nubes se traslapan. La dispersión por clases (knn_clases_mag_depth.png, con los mismos colores de las veces pasadas) enseña justo eso, Guatemala en su zona profunda y los otros dos mezclados entre los sismos de poca profundidad.

Como verificación final se implementó un KNN a mano (distancia euclidiana y votación por mayoría, la misma lógica del classification.org del material de la materia) y se comparó contra sklearn sobre una muestra de 200 sismos del test, ambos coinciden, lo que confirma que el proceso con librería fue correcto. 

## Conclusión

Para dar respuesta a lo planteado en la practica, digamos que es algo parcial ya que la huella de cómo se registró el sismo sí alcanza para separar Guatemala del resto (se clasifica casi sin error por su profundidad), pero no alcanza para distinguir EEUU de MEXICO, que se confunden entre sí porque ambos son sismos de poca profundidad y con coberturas parecidas. El KNN supera al modelo base que siempre predice la clase mayoritaria, así que sí aprende algo real, pero la confusión entre esas dos clases deja ver el límite de la huella de registro, sin latitud ni longitud alcanza para separar sismos profundos de sismos de poca profundidad, no para distinguir países que comparten el mismo régimen de profundidad.


## NOTAS

1. Se repaso el material de classification.org y se usó como referencia
2. Los valores exactos de accuracy, k y matriz quedan en las capturas de ejecución
3. Referencias consultadas:
   - https://github.com/ppGodel/data_mining (classification.org con el KNN a mano y la dispersión por clase)
   - https://en.wikipedia.org/wiki/K-nearest_neighbors_algorithm (conceptos de KNN)
   - https://en.wikipedia.org/wiki/Cross-validation_(statistics) (validación cruzada y por qué las decisiones se toman en entrenamiento)
   - https://scikit-learn.org/stable/modules/preprocessing.html (por qué escalar en métodos que viven de distancias)
