# Práctica 3 Visualización de Datos 

El script de esta práctica es `Visualizacion_Datos_Earthquake.py`. Todas las gráficas se guardan en la carpeta de `Graficas` y pueden verse aquí mismo en el repositorio.

La práctica pide al menos 5 tipos de gráficas diferentes y en este caso se generaron: histogramas, pasteles, dispersión, barras y de línea. 


---

## 1. Histogramas

Se hicieron en un ciclo para `mag`, `depth`, `nst` y `rms`, cada uno con un color distinto para distinguirlos entre sí.

- `hist_mag.png`: deja ver que la mayoría de los sismos son pequeños y los grandes no tan comunes.
- `hist_depth.png`: casi todos los sismos son superficiales, con una cola larga de pocos sismos muy profundos.
- `hist_nst.png` y `hist_rms.png`: `nst` es el número de estaciones que registraron el sismo (a más estaciones, mejor queda ubicado), y `rms` es el residuo medio en segundos entre el tiempo de llegada observado y el calculado, mientras más bajo, más confiable es la ubicación. Con los histogramas se ve que la mayoría de los sismos se registran con pocas decenas de estaciones y con residuos pequeños.

Se usaron 25 barras porque con 50 se veían algo amontonado.

---

## 2. Pasteles (proporciones por categoría)

Se hicieron en un ciclo para `pais` y `net_clean`. Se eligió el pastel porque son pocas categorías (4) y la proporción de cada una se ve de inmediato.

- `pastel_pais.png`: muestra que la mayoría de los sismos del catálogo ocurren en EEUU, seguido de México, y muy pocos en Centroamérica (Recordar que estamos analizando principalmente a México y alrededores). 
- `pastel_net_clean.png`: muestra qué redes registran más sismos (tx y us concentran la mayor parte).

Se quitaron las categorías con muy pocos sismos (menos de 30) porque su rebanada ni se vería bien en la gráfica. 

---

## 3. Dispersión: mapa de sismos

`mapa.png` grafica latitud contra longitud, que es básicamente un mapa de donde hay sismos (de hecho se aprecia mas o menos la forma de México). Cada país va con su color (EEUU azul, México verde, Guatemala naranja, Honduras rojo).

Se usaron puntos chiquitos y con transparencia (alpha) porque con casi 8000 sismos, con puntos normales todo se vuelve una mancha y no se aprecian las zonas donde se concentra más actividad sismica.

Obs: los puntos azules (EEUU) son los más numerosos (aunque no se aprecie tal vez mucho porque estan muy juntos) y se acumulan en zonas compactas al norte del mapa, los verdes (MEXICO) forman una franja alargada en diagonal, los naranjas (GUATEMALA) quedan en un grupo compacto al sur, y los rojos (HONDURAS) son pocos y aparecen dispersos en la esquina sureste. La cantidad de puntos de cada color concuerda con los conteos de las barras y el pastel por país. 

---

## 4. Barras: sismos por año

`barras_anio.png` cuenta cuántos sismos hubo por año, con un color distinto por año para distinguir bien.

Obs: 2026 sale más bajo porque el año está incompleto (solo hasta agosto), no es un error de los datos.

---

## 5. Barras: magnitud media por país

`barras_mag_pais.png` compara qué tan fuertes son en promedio los sismos de cada zona. Cada país lleva el mismo color que en el mapa para poder relacionar ambas gráficas.

Obs: EEUU tiene la magnitud media más baja (muchos sismos chicos) y México y Guatemala tienen promedios más altos (menos sismos pero más fuertes).

---

## 6. Línea: sismos por mes

`linea_mes.png` muestra el conteo mensual para ver la tendencia en el tiempo con más detalle que la gráfica por año, y como son alrededor de 80 meses, se puso una etiqueta cada 12 para organizar mejor.

La actividad mensual se mantiene "más o menos" constante, con picos aislados con muchos sismos en la misma zona en pocos días (esto apunta a ser réplicas). El último punto cae de golpe no porque haya bajado la actividad, sino porque ese mes está incompleto (los datos llegan solo hasta agosto de 2026).

---

## 7. Notas

1. Se reutilizó la función `categorize_pais` de la Práctica 2 para poder colorear el mapa y hacer las barras por país.
2. No se repitió el boxplot aquí porque ya se generó en la Práctica 2 (`boxplot_pais.png` y `boxplot_red.png`).
3. Referencias consultadas:
   - https://matplotlib.org/stable/plot_types/index.html (para elegir el tipo de gráfica adecuado según el dato)
4. ACLARACIÓN IMPORTANTE: en practicas anteriores se olvidó mencionar el como se sabe que es cada columna del dataset, los links de referecia son:
   - https://earthquake.usgs.gov/data/comcat/data-eventterms.php?spm=a2ty_o01.29997173.0.0.717c55fbqntSZS
   - https://earthquake.usgs.gov/fdsnws/event/1/?spm=a2ty_o01.29997173.0.0.717c55fbqntSZS
   - https://earthquake.usgs.gov/data/comcat/?spm=a2ty_o01.29997173.0.0.717c55fbqntSZS
