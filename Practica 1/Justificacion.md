# Práctica 1 – Limpieza de Datos: Justificación de decisiones

**Dataset:** `Earthquake.csv` (sismos registrados en México y alrededores por el USGS entre 2020 y 2026)
**Script completo:** `Clean_Earthquake.py`
**Resultado:** `Earthquake_limpio.csv` (el archivo original **nunca** se modifica)

---

## 1. Descripción general del dataset

El archivo original contiene **7,893 filas (sismos)** y **22 columnas**, con registros del **2 de enero de 2020 al 14 de agosto de 2026**. Cada fila es un sismo con su fecha y hora (`time`), ubicación (`latitude`, `longitude`), profundidad (`depth`), magnitud (`mag`), tipo de magnitud medida (`magType`), red sísmica que lo registró (`net`), errores de medición y un texto que indica el lugar (`place`).




---

## 2. Lo que reveló el diagnóstico

Antes de limpiar, se hicieron pruebas y en ellas se desarrolló un pequeño script de diagnóstico para visualizar los datos e identificar que era lo que se debía incluir en la limpieza (también se usó levemente excel para visualizar un poco), y al final este script de diagnóstico se incluyo en la versión final del programa junto con la limpieza (En resumen: Earthquake.csv -> Clean_Earthquake.py -> Earthquake_limpio.csv). En el diagnóstico podemos destacar los siguientes puntos:

1. **Fechas como texto:** `time` y `updated` se cargaban como texto, no como fechas reales.
2. **Valores nulos:** `nst` (1,188 nulos), `magError` (133), `gap` (2), `dmin` (2), `rms` (2).
3. **Sin duplicados:** 0 filas duplicadas y 0 IDs repetidos (verificado, no hubo que eliminar nada).
4. **Columnas inútiles o redundantes:** `locationSource` es 100% idéntica a `net`; `type` solo contiene "earthquake"; `status` es 99.99% "reviewed".
5. **Categorías inconsistentes en `magType`:** el mismo tipo de magnitud aparecía con nombres distintos: `ml`, `ml(texnet)`, `mlv`, `mlr`.
6. **Ceros sospechosos:** columnas como `magError`, `rms`, `dmin`, `magNst` y `horizontalError` tenían ceros exactos que no representan una medición real, sino "la red no reportó este dato".
7. **Profundidades negativas:** 8 filas con profundidad entre -1.61 y -0.01 km.
8. **Categorías muy pequeñas:** redes y tipos con 1 a 11 registros (`se`, `ew`, `nm`, `slm`, `md`, `mh`, `mwb`).

---

## 3. Decisiones de limpieza aplicadas (con justificación)

### 3.1 Convertir fechas a fechas reales
**Qué se hizo:** `time` y `updated` se convirtieron de texto a fecha (`datetime`), estandarizadas en UTC y sin zona horaria para evitar problemas de compatibilidad.
**Por qué:** con fechas como texto no se puede ordenar cronológicamente ni preparar la práctica de series de tiempo).

### 3.2 Duplicados
**Qué se hizo:** se verificaron duplicados por id; se encontraron 0 por lo que no se eliminó nada.
**Por qué:** un registro duplicado haría que un sismo "cuente doble" lo que perjudicaría a la estadistica.




### 3.3 Normalizar texto
**Qué se hizo:** se quitaron espacios sobrantes y se unificaron minúsculas en columnas de texto (`net`, `magType`, `magSource`, `place`, `id`).
**Por qué:** evita que por ejemplo "Texas" y "texas " cuenten como categorías diferentes.

### 3.4 Eliminar columnas que no aportan información
**Qué se hizo:** se eliminaron 3 columnas:
- `locationSource`: idéntica a `net` en el 100% de las filas (verificado por el script), conservar ambas es guardar dos veces lo mismo.
- `type`: el 100% de los valores es "earthquake", una columna donde todo es igual no sirve para comparar ni agrupar.
- `status`: 99.99% es "reviewed" (7,892 de 7,893), al ser prácticamente lo mismo, no aporta variación útil.

**Por qué:** las columnas sin variabilidad solo agregan ruido.

### 3.5 Unificar tipos de magnitud (`magType`)
**Qué se hizo:** `ml(texnet)` (144), `mlv` (11) y `mlr` (8) se unificaron en `ml`.
**Por qué:** todas son "magnitud local" (la misma escala), solo que reportadas con etiquetas distintas por redes diferentes, esto sería como tener "kilo", "kg" y "kilogramo": es lo mismo escrito diferente. Después de unificar, `ml` pasó de 5,372 a 5,535 registros.

### 3.6 Filtro de valores físicamente imposibles
**Qué se hizo:** se verificó que la latitud esté entre -90 y 90, la longitud entre -180 y 180 y la magnitud sea mayor a 0. Se detectaron 0 filas fuera de rango (queda documentado).
**Por qué:** una latitud de 999 grados no existe en el planeta, este filtro protege contra errores de sensor.

### 3.7 Profundidades negativas: conservar y documentar
**Qué se hizo:** las 8 filas con profundidad negativa no se eliminaron, se conservan y se documentan.
**Por qué:** según la documentación del USGS, la profundidad puede medirse respecto a distintas referencias (nivel del mar, geoide, elevación de las estaciones), por lo que un valor ligeramente negativo es un artefacto de medición, no un sismo imposible. **Eliminarlas perdería información válida**.

### 3.8 Ceros sospechosos tratados como "desconocido"
**Qué se hizo:** los ceros exactos en `magError` (144), `horizontalError` (4), `rms` (11), `magNst` (1) y `dmin` (925) se convirtieron a valor faltante (NaN).
**Por qué:** un error de medición de "cero" no es real, significa que la red no reportó el dato. Dejarlo en cero sesgaría (jalaría hacia abajo) la mediana y las estadísticas.



### 3.9 Rellenar valores faltantes con la mediana (imputación)
**Qué se hizo:** los valores faltantes de cada columna se rellenaron con su **mediana**:
- `nst`: 1,188 nulos -> mediana 31
- `dmin`: 927 -> 0.111
- `magError`: 277 -> 0.1
- `rms`: 13 -> 0.28
- `gap`: 2 -> 69
- `horizontalError`: 4 -> 1.0155
- `magNst`: 1 -> 24

**Por qué:** la mayoría de los análisis y modelos no funcionan con celdas vacías, se usa la mediana y no el promedio porque estas variables tienen valores extremos (por ejemplo, sismos medidos por 658 estaciones) que deformarían el promedio. Un link de referencia acerca de la imputación: https://link.springer.com/article/10.1186/s40537-020-00313-w

### 3.10 Crear versiones "seguras" de las categorías (`clean`)
**Qué se hizo:** se crearon 3 columnas nuevas: `net_clean`, `magSource_clean` y `magType_clean`. En ellas, las categorías con menos de 30 registros se agrupan bajo la etiqueta `other`.
**Por qué:** comparar un grupo de 3,535 sismos contra un grupo de 1 sismo no es estadísticamente válido en pruebas como ANOVA o clasificación. Las columnas nuevas dejan grupos listos para usar:



| net_clean | Registros |
| --- | --- |
| tx | 3,535 |
| us | 2,826 |
| ci | 1,528 |
| other | 4 |

Las columnas originales (`net`, `magSource`, `magType`) se conservan intactas por si se quieren usar.

### 3.11 Marcar profundidades estimadas (`profundidad_estimada`)
**Qué se hizo:** se creó una columna que marca con `True` los sismos cuya profundidad es exactamente 5.0 o 10.0 km (1,457 filas, 18.5%).
**Por qué:** cuando el USGS no puede calcular la profundidad exacta, asigna un valor por defecto (5 o 10 km). Esta columna permite identificar cuáles profundidades son "estimadas" para que prácticas futuras (modelos, clustering) puedan filtrarlas si lo necesitan, sin perder esas filas.

### 3.12 Ordenar cronológicamente
**Qué se hizo:** todo el dataset se ordenó por `time`, del sismo más antiguo al más reciente.
**Por qué:** para tener un orden claro y puede ayudar a futuras practicas.

### 3.13 Exportar sin tocar el original
**Qué se hizo:** el resultado se guardó en un archivo **nuevo** llamado `Earthquake_limpio.csv` (codificación UTF-8 compatible con Excel). `Earthquake.csv` queda intacto.
**Por qué:** no se sabe si el archivo original será necesario para cualquier cosa.

---



## 4. Resumen final

| Aspecto | Original | Limpio |
| --- | --- | --- |
| Filas | 7,893 | 7,893 (no se perdió ningún sismo) |
| Columnas | 22 | 23 (se eliminaron 3 y se crearon 4) |
| Valores nulos | 1,327 | **0** |
| Fechas | texto | fechas reales y ordenadas |
| Duplicados | 0 | 0 |

---




