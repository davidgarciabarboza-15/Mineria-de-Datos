# Práctica 7 Agrupamiento de Datos

La tarea fue descubrir grupos naturales en el catálogo con K-Means y evaluar qué fue lo que encontró.

Las gráficas quedan como kmeans_barrido_k.png (inercia y silhouette por cada k), kmeans_clusters_mag_depth.png (los grupos finales en el plano mag-depth con sus centroides) y kmeans_iter_inicio.png y kmeans_iter_final.png (el inicio y la convergencia del K-Means a mano).

## Qué cambia respecto a la práctica 6

En la clasificación de la práctica 6 había una etiqueta que guiaba el ajuste, pero aquí no, k-means solo ve las características numéricas y tiene que descubrir los grupos por su cuenta. La etiqueta de país (la de la práctica 2) se recrea en el script pero se usa únicamente al final, en una tabla cruzada, para leer qué encontraron los clusters, nunca participa en el ajuste. Al ser aprendizaje no supervisado, aquí no hay partición train/test porque el modelo no predice, solo describe, y tampoco se excluyó a Honduras, cuyos 34 sismos se suman al montón como cualquier otro punto.

Las características son las mismas 7 de registro de la práctica 6 (depth, mag, nst, gap, dmin, rms, magNst), escaladas con StandardScaler por la misma razón de la práctica 6, k-means se basa de distancias y sin escalar el gap, que va de 0 a 360, dominaría el cálculo sobre las demás. Latitud y longitud se dejaron fuera otra vez porque el país sale de la geografía, así que agrupar por geografía y luego comparar contra país sería redescubrir el mapa y no la estructura de los datos.

## La elección de k

Se barrió k de 2 a 8 calculando en cada paso la inercia y el silhouette.

La inercia (la suma de las distancias al cuadrado de cada punto a su centroide) siempre baja al subir k, por eso no elige sola, su gráfica sirve para buscar el codo. El silhouette (qué tan bien queda cada punto entre su grupo y el vecino, de -1 a 1) se calculó sobre una muestra de 2000 sismos porque con los casi 8000 completos el cálculo seria muy pesado.

El silhouette se mantiene en una meseta de alrededor de 0.52 para k=2, 3 y 4, y cae a cerca de 0.38 desde k=5. El máximo elige k=2, aunque por una diferencia mínima, de 0.5203 contra 0.5200 de k=4. Ese empate técnico también es información, porque los datos toleran lecturas de 2 a 4 grupos con definición parecida y la estructura más fuerte y estable es la de dos, mientras que de 5 en adelante los grupos extra son divisiones menos definidas.

## Los 2 grupos encontrados

Con el perfil de cada cluster, o sea los promedios de cada característica, los grupos se pueden nombrar directo. El cluster 0 junta 2135 sismos del régimen profundo y grande, con profundidad media de unos 38 km, magnitud de unos 4.4 y más estaciones reportando (nst unos 54, magNst unos 80) pero con cobertura más holgada (gap unos 148, dmin unos 1.4 km). El cluster 1 junta 5758 sismos del régimen somero de red densa, con profundidad de unos 7 km, magnitud de unos 2.9, menos estaciones y prácticamente encima del evento (dmin unos 0.1 km, gap unos 68). En la gráfica mag-depth la separación se lee en la profundidad, porque solo el cluster 0 sube a la zona profunda (la columna de magnitudes 4 a 5 que alcanza hasta unos 270 km) mientras el cluster 1 se queda pegado a profundidades bajas en casi todo el rango de magnitud, y en lo somero los dos grupos conviven, que es justo por lo que los clusters no salen perfectamente compactos.

## La lectura de los clusters contra los países

La tabla cruzada deja ver que la frontera natural no coincide con las fronteras políticas, el cluster 1 es casi todo EEUU (5048 de 5758) más 696 sismos de México, el cluster 0 concentra a México (1885), Guatemala (194) y Honduras (33), con apenas 23 sismos de EEUU. O sea que México aparece en los dos grupos, y vemos que sus sismos profundos y grandes, los de la placa que se hunde bajo el continente, caen en el régimen regional, y sus sismos someros en el de red densa. Y Guatemala, que en la práctica 6 se separaba sola por profundidad, aquí queda en el mismo grupo que México, con k=2 lo que define al grupo es el régimen completo (profundidad, tamaño y cobertura), no la profundidad sola.

La conclusión que queda al ver esto con datos propios es que los grupos naturales del catálogo son regímenes sísmicos y de registro, no países. La etiqueta que ya teníamos sirve para leer y nombrar esa diferencia, no para calificar al modelo como si fuera clasificación.


## Verificación a mano

Como en la prática 6 con el KNN, se implementó un k-means a mano (proponer centroides, asignar cada punto al más cercano, recalcular los centroides como el promedio de sus miembros y repetir hasta que nadie se mueva) y se comparó contra sklearn, ambos llegaron a exactamente la misma inercia, 33497.2, lo que confirma que la librería y la lógica a mano llegan a la misma solución. Los png de inicio y convergencia dejan ver cómo los grupos se forman en pocas iteraciones.

Un detalle visible en los png es que en la corrida a mano los números de cluster salen intercambiados respecto a sklearn (lo que uno llama 0, el otro lo llama 1), en agrupamiento los números son arbitrarios, y por eso exactamente la comparación entre las dos versiones se hace con la inercia y no etiqueta por etiqueta.

## Notas

1. Del clustering.org del material de la materia se tomo en cuenta: la lógica del K-Means a mano como verificación y la idea de los png por iteración, recortada a inicio y final.
2. Referencias consultadas:
   - https://github.com/ppGodel/data_mining (material de la materia; clustering.org con el K-Means a mano)
   - https://en.wikipedia.org/wiki/K-means_clustering (concepto de K-Means: centroides, asignación y convergencia)
   - https://en.wikipedia.org/wiki/Silhouette_(clustering) (silhouette y cómo se interpreta)
   - https://scikit-learn.org/stable/modules/clustering.html (K-Means en sklearn, inercia y consideraciones del barrido)
