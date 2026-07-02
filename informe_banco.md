# Proyecto EDA y modelización con Python: campañas de marketing bancario

## 1. Objetivo

Este proyecto realiza un análisis exploratorio, inferencial y predictivo sobre campañas de marketing directo de una institución bancaria. El objetivo principal es estudiar qué características de los clientes y de las campañas están asociadas con la suscripción de un depósito a plazo (`y = yes`) y construir modelos que ayuden a priorizar clientes con mayor probabilidad de conversión.

El análisis incluye limpieza de datos, análisis descriptivo, visualizaciones, modelos de regresión logística, análisis de multicolinealidad, validación temporal, tablas de deciles, modelos sobre segmentos específicos y comparación con un modelo no lineal basado en Random Forest.

## 2. Estructura del repositorio

```text
PROYECTO_MARKETING_BANCO/
├── README.md
├── requirements.txt
├── DATOS/
│   ├── BRUTOS/
│   │   ├── bank-additional.csv
│   │   └── customer-details.xlsx
│   └── PROCESADOS/
│       ├── bank_marketing_limpio.csv
│       ├── customer_details_limpio.csv
│       └── bank_customer_merged_limpio.csv
├── CODIGO/
│   └── marketing_bancos.py
└── INFORMES/
    ├── tablas_resumen_eda.xlsx
    ├── resultados_regresiones.txt
    └── GRAFICOS/
```

### Mejora aplicada sobre el código

En la versión revisada del proyecto se ha puesto especial énfasis en la limpieza y simplificación del código. Las principales mejoras aplicadas son:

- Se han eliminado importaciones duplicadas y librerías no utilizadas.
- Se han evitado nombres de funciones con caracteres especiales, por ejemplo sustituyendo nombres con `ñ` por alternativas más estándar.
- Se han creado constantes globales para las listas de variables usadas en los modelos, evitando repetir listas de columnas en distintas funciones.
- Se ha centralizado la creación de modelos, preprocesadores, métricas, tablas de umbrales y tablas de deciles.
- Se ha reducido la repetición de bloques de entrenamiento y evaluación de modelos.
- Se ha incorporado imputación dentro del `Pipeline` de `sklearn`, usando `SimpleImputer`, para evitar que los datos de test influyan en el cálculo de medianas o categorías frecuentes.
- Se ha simplificado la exportación a Excel, dejando un archivo final más directo y fácil de revisar.

Estas modificaciones hacen que el proyecto sea más mantenible, más fácil de corregir y más cercano a una estructura profesional de análisis de datos.

## 3. Datos utilizados

Se han utilizado dos fuentes de información:

1. `bank-additional.csv`: contiene información de campañas de marketing bancario, características de contacto, variables socioeconómicas, resultado de campañas anteriores y la variable objetivo `y`.
2. `customer-details.xlsx`: contiene información adicional de clientes, distribuida en varias hojas correspondientes a distintos años.

Tras limpiar y unir ambos ficheros por el identificador del cliente (`id_` / `ID`), se obtuvo un dataset analítico de **43,000 registros**.

La variable objetivo se transformó en una variable binaria llamada `subscribed`:

- `subscribed = 1`: el cliente suscribió el producto.
- `subscribed = 0`: el cliente no suscribió el producto.

## 4. Limpieza y transformación de datos

Antes de realizar el análisis descriptivo y la modelización, se aplicó un proceso de limpieza y transformación para asegurar que las variables tuvieran un formato correcto, que los dos ficheros pudieran unirse correctamente y que el dataset final fuera apto para el análisis estadístico y predictivo.

Las principales transformaciones aplicadas fueron las siguientes:

### 4.1 Eliminación de columnas sin valor analítico

Se eliminaron columnas índice generadas automáticamente, como las columnas `Unnamed`. Estas columnas suelen aparecer al guardar ficheros CSV desde pandas o Excel incluyendo el índice del dataframe original.

Estas variables no aportan información real sobre los clientes ni sobre las campañas, por lo que mantenerlas podría introducir ruido en el análisis o incluso provocar errores en procesos posteriores.

### 4.2 Conversión de variables numéricas

Algunas variables económicas venían almacenadas como texto y utilizaban coma decimal en lugar de punto decimal. Por ejemplo:

- `cons.price.idx`
- `cons.conf.idx`
- `euribor3m`
- `nr.employed`

Estas columnas se transformaron a formato numérico para poder calcular medias, correlaciones, gráficos, modelos estadísticos y modelos predictivos.

Esta transformación es necesaria porque, si una variable numérica permanece como texto, Python no puede interpretarla correctamente en operaciones matemáticas ni en algoritmos de machine learning.

### 4.3 Conversión de fechas

La columna de fecha de contacto aparecía en formato texto y con el mes escrito en español. Por ello, se creó una función específica para convertir fechas como `2-agosto-2019` a un formato de fecha real interpretable por pandas.

A partir de esa fecha transformada se crearon dos nuevas variables:

- `contact_month`: mes del contacto.
- `contact_year`: año del contacto.

Estas variables permiten analizar si existen diferencias de conversión según el momento temporal de la campaña. Por ejemplo, pueden ayudar a detectar meses con mejor respuesta comercial o posibles patrones estacionales.

### 4.4 Preparación del fichero de clientes

El fichero `customer-details.xlsx` contenía la información de clientes distribuida en varias hojas. Por ello, se concatenaron todas las hojas en un único dataframe, manteniendo una columna auxiliar con el año de procedencia de cada hoja.

Además, se renombró la columna `ID` a `id_` para que coincidiera con el identificador del fichero bancario. Esta transformación fue necesaria para poder unir ambos datasets de forma consistente.

### 4.5 Unión de los datasets

Una vez limpiados los identificadores, se unieron los datos bancarios y los datos de clientes mediante una unión uno a uno usando `id_`.

Esta unión permitió construir un único dataset analítico con información de tres tipos:

- Información de la campaña bancaria.
- Información socioeconómica y de contacto.
- Información demográfica y de comportamiento del cliente.

La unión se realizó con validación `one_to_one`, lo que permite comprobar que cada cliente aparece una sola vez en cada fuente. Esto ayuda a evitar duplicidades y errores en el dataset final.

### 4.6 Tratamiento de valores faltantes

Los valores faltantes se trataron de forma distinta según el tipo de variable:

- En variables numéricas se imputó la mediana.
- En variables categóricas se sustituyeron los valores ausentes por la categoría `desconocido`.

La mediana se utilizó porque es una medida más robusta que la media cuando existen valores extremos. Esto es especialmente útil en variables como ingresos, duración de llamada o número de contactos, donde pueden existir observaciones muy altas.

En las variables categóricas se usó `desconocido` para no eliminar registros y para conservar la información de que el dato no estaba disponible. En algunos casos, la ausencia de información también puede tener valor analítico.

Además, cuando se imputaron variables numéricas, se crearon indicadores de ausencia para identificar qué registros tenían originalmente valores faltantes. Esto permite que los modelos puedan capturar si la falta de información está asociada con la probabilidad de suscripción.

### 4.7 Creación de la variable objetivo

Se creó la variable `subscribed` a partir de la variable original `y`.

La transformación aplicada fue:

- `yes` → `1`
- `no` → `0`

Esta conversión es necesaria porque los modelos de clasificación necesitan una variable objetivo binaria en formato numérico. En este caso, `1` representa que el cliente suscribió el producto y `0` que no lo hizo.

### 4.8 Creación de variables derivadas

Se crearon varias variables adicionales para enriquecer el análisis:
- `age_group`: agrupa la edad en tramos. Esto facilita interpretar diferencias de conversión por grupos de edad y no solo por edad exacta.
- `duration_min`: transforma la duración de la llamada de segundos a minutos. Esta versión es más interpretable para el análisis descriptivo. No obstante, esta variable debe interpretarse con cautela en modelos predictivos, ya que la duración de la llamada se conoce después del contacto.
- `total_children_home`: suma `Kidhome` y `Teenhome`, creando una medida del número total de hijos en el hogar. Esto simplifica la información familiar del cliente.
- `customer_tenure_days`: mide la antigüedad del cliente tomando como referencia la fecha más reciente disponible en los datos. Esta variable permite analizar si los clientes más antiguos tienen una probabilidad distinta de suscripción.
- `income_group`: clasifica los ingresos en cuartiles. Esto facilita comparar tasas de conversión entre niveles de ingresos sin depender únicamente del valor exacto de la renta.
- `contacto_previo`: identifica si el cliente había sido contactado previamente. Se creó a partir de `pdays`, considerando que valores como `999` indicaban ausencia de contacto previo.

### 4.9 Consideración sobre `contacto_previo`

Aunque `contacto_previo` se creó como una variable derivada útil para el análisis exploratorio, posteriormente se detectó que estaba casi perfectamente correlacionada con `pdays`. Por este motivo, en los modelos inferenciales finales se decidió excluir `contacto_previo` para evitar problemas de multicolinealidad.

Esta decisión permitió mantener un modelo más estable e interpretable, conservando `pdays` como variable explicativa.

## 5. Análisis descriptivo

La variable objetivo está claramente desbalanceada:

- Total de registros: **43,000**.
- Tasa global de suscripción: **11.27%**.
- Tasa de no suscripción: **88.73%**.

Debido al desbalance de la variable objetivo, la evaluación de los modelos no puede basarse únicamente en la exactitud global del modelo. Esta métrica puede resultar engañosa, ya que un modelo que predijera mayoritariamente la clase “no suscribe” obtendría un valor elevado de acierto, pero tendría poca utilidad para identificar clientes con potencial real de conversión.

Por ello, se analizaron métricas centradas en la clase positiva, es decir, en los clientes que sí suscriben el producto:
- Precisión de la clase positiva (`precision`): mide, entre los clientes que el modelo clasifica como posibles suscriptores, qué proporción realmente suscribe. Es útil para saber si los clientes seleccionados por el modelo son contactos de calidad.
- Sensibilidad o capacidad de detección de la clase positiva (`recall`): mide, entre todos los clientes que realmente suscriben, qué proporción consigue detectar el modelo. Es importante cuando el objetivo es no perder demasiados clientes potenciales.
- Puntuación F1 de la clase positiva (`f1-score`): combina precisión y sensibilidad en una sola métrica. Es útil cuando se busca un equilibrio entre contactar clientes con alta probabilidad de conversión y detectar el mayor número posible de suscriptores.
- Área bajo la curva ROC (`ROC AUC`): mide la capacidad general del modelo para ordenar correctamente a los clientes según su probabilidad de suscripción, independientemente del umbral de decisión utilizado.
- Precisión media (`Average Precision`): resume el comportamiento del modelo en la curva precisión-sensibilidad. Es especialmente útil en problemas con clases desbalanceadas, porque pone más atención en el rendimiento sobre la clase positiva.
- Matrices de confusión: permiten ver cuántos clientes se clasifican correctamente e incorrectamente en cada grupo: verdaderos positivos, falsos positivos, verdaderos negativos y falsos negativos.
- Comparación de umbrales: permite estudiar cómo cambian la precisión, la sensibilidad y la puntuación F1 al modificar el punto de corte usado para clasificar a un cliente como posible suscriptor. Esto es importante porque el umbral estándar de 0.50 no siempre es el más adecuado en campañas comerciales.
- Tablas de deciles y mejora acumulada (`lift`): permiten evaluar la utilidad del modelo desde una perspectiva de negocio. Estas tablas muestran si el modelo es capaz de concentrar los clientes con mayor probabilidad de conversión en los primeros grupos de prioridad.

## 6. Modelo predictivo inicial: regresión logística

El primer modelo predictivo se estimó mediante una regresión logística utilizando `sklearn`. Este modelo se tomó como punto de partida porque es un algoritmo adecuado para problemas de clasificación binaria y, además, permite obtener una primera referencia interpretable del rendimiento predictivo.

El objetivo del modelo era estimar la probabilidad de que un cliente suscribiera el producto bancario. Para ello, la variable objetivo fue `subscribed`, donde:

- `1` indica que el cliente sí suscribió el producto.
- `0` indica que el cliente no suscribió el producto.

La regresión logística genera una probabilidad estimada para cada cliente. Posteriormente, esa probabilidad se transforma en una predicción binaria utilizando un umbral de clasificación. En este primer modelo se utilizó el umbral estándar de `0.50`: si la probabilidad estimada era igual o superior a 0.50, el cliente se clasificaba como posible suscriptor; en caso contrario, se clasificaba como no suscriptor.

### Resultados principales

| Métrica                      |  Valor |
| ---------------------------- | -----: |
| Exactitud global             | 0.9015 |
| Área bajo la curva ROC       | 0.7826 |
| Precisión clase positiva     | 0.7235 |
| Sensibilidad clase positiva  | 0.2031 |
| Puntuación F1 clase positiva | 0.3172 |

El modelo obtiene una exactitud global del **90.15%**, lo que inicialmente podría parecer un resultado muy alto. Sin embargo, esta métrica debe interpretarse con cautela, ya que la variable objetivo está fuertemente desbalanceada: la mayoría de los clientes no suscriben el producto. En este contexto, un modelo puede alcanzar una exactitud elevada simplemente clasificando correctamente a la mayoría de los clientes como “no suscribe”.

Por este motivo, es más importante analizar el comportamiento del modelo sobre la clase positiva, es decir, sobre los clientes que realmente suscriben.

### Matriz de confusión

|         | Predicho no | Predicho sí |
| ------- | ----------: | ----------: |
| Real no |        9445 |          94 |
| Real sí |         965 |         246 |

La matriz de confusión muestra cuatro tipos de resultados:

- **Verdaderos negativos**: 9445 clientes que no suscribieron y fueron correctamente clasificados como “no”.
- **Falsos positivos**: 94 clientes que no suscribieron, pero fueron clasificados como posibles suscriptores.
- **Falsos negativos**: 965 clientes que sí suscribieron, pero el modelo los clasificó como “no”.
- **Verdaderos positivos**: 246 clientes que sí suscribieron y fueron correctamente detectados por el modelo.

Estos valores muestran que el modelo es muy conservador al predecir la clase positiva. Identifica pocos clientes como posibles suscriptores, pero cuando lo hace suele acertar bastante.

### Interpretación de las métricas

La precisión de la clase positiva fue de **0.7235**. Esto significa que, entre los clientes que el modelo clasificó como posibles suscriptores, aproximadamente el **72.35%** realmente suscribió el producto. Desde un punto de vista comercial, esto indica que los clientes seleccionados por el modelo tienen una calidad relativamente alta.

Sin embargo, la sensibilidad de la clase positiva fue de solo **0.2031**. Esto significa que el modelo solo detectó alrededor del **20.31%** de todos los clientes que realmente terminaron suscribiendo. Dicho de otra forma, el modelo dejó sin identificar a casi el **79.69%** de los suscriptores reales.

La puntuación F1 fue de **0.3172**, lo que refleja este desequilibrio entre una precisión alta y una sensibilidad baja. El modelo es bueno cuando decide señalar a un cliente como suscriptor, pero detecta una proporción pequeña del total de suscriptores.

El área bajo la curva ROC fue de **0.7826**, lo que indica que el modelo sí tiene una capacidad razonable para ordenar a los clientes según su probabilidad de suscripción. Es decir, aunque el umbral de 0.50 no detecta muchos positivos, las probabilidades estimadas por el modelo contienen información útil para diferenciar clientes más y menos propensos.

### Conclusión del modelo inicial

El modelo inicial de regresión logística ofrece una primera aproximación útil, pero tiene una limitación clara: con el umbral estándar de 0.50 detecta pocos clientes suscriptores. Esto se debe principalmente al desbalance de la variable objetivo y a que el modelo tiende a favorecer la clase mayoritaria.

Desde el punto de vista de negocio, este modelo puede ser útil si el objetivo es contactar solo a clientes con una probabilidad alta de conversión, minimizando falsos positivos. Sin embargo, si el objetivo de la campaña es captar un mayor número de posibles suscriptores, será necesario ajustar el umbral de decisión, probar modelos balanceados o comparar con algoritmos más flexibles.

Por esta razón, en los apartados posteriores se analizaron distintos umbrales de clasificación, modelos balanceados, tablas de deciles y modelos alternativos como Random Forest.

## 7. Modelo balanceado

Después de estimar el modelo base de regresión logística, se entrenó una segunda versión incorporando ajuste de pesos mediante `class_weight="balanced"`.

Este ajuste se utiliza cuando la variable objetivo está desbalanceada. En este caso, la clase mayoritaria es “no suscribe” y la clase minoritaria es “sí suscribe”. Si no se corrige este desequilibrio, el modelo tiende a favorecer la clase mayoritaria, consiguiendo una exactitud global alta, pero detectando pocos clientes que realmente suscriben.

Con `class_weight="balanced"`, el algoritmo asigna más peso a la clase minoritaria durante el entrenamiento. Es decir, los errores cometidos sobre clientes que sí suscriben pasan a tener más importancia. El objetivo no es necesariamente aumentar la exactitud global, sino mejorar la capacidad del modelo para detectar clientes positivos.

### Comparación de resultados

| Modelo     | Área bajo la curva ROC | Precisión media | Exactitud global | Precisión clase positiva | Sensibilidad clase positiva | Puntuación F1 clase positiva |
| ---------- | ---------------------: | --------------: | ---------------: | -----------------------: | --------------------------: | ---------------------------: |
| Base       |                 0.7826 |          0.4544 |           0.9015 |                   0.7235 |                      0.2031 |                       0.3172 |
| Balanceado |                 0.7819 |          0.4510 |           0.7806 |                   0.2920 |                      0.6656 |                       0.4059 |

El área bajo la curva ROC se mantiene prácticamente igual en ambos modelos: **0.7826** en el modelo base y **0.7819** en el modelo balanceado. Esto indica que la capacidad general de ordenar clientes según su probabilidad de suscripción apenas cambia.

Sin embargo, sí cambia de forma importante la forma en que el modelo clasifica a los clientes. El modelo base es más conservador: predice pocos positivos, pero cuando los predice suele acertar más. Por eso alcanza una precisión de la clase positiva del **72.35%**, pero solo detecta el **20.31%** de los suscriptores reales.

El modelo balanceado hace lo contrario: identifica muchos más clientes como posibles suscriptores. Por ello, la sensibilidad de la clase positiva aumenta de **20.31%** a **66.56%**. Es decir, consigue detectar aproximadamente dos tercios de los clientes que realmente suscriben.

La contrapartida es que la precisión baja de **72.35%** a **29.20%**. Esto significa que, entre los clientes que el modelo balanceado clasifica como posibles suscriptores, una proporción mayor finalmente no suscribe. En términos comerciales, el modelo balanceado genera más oportunidades, pero también más contactos poco efectivos.

La exactitud global también baja, pasando de **90.15%** a **78.06%**. Esta caída es esperable, ya que el modelo deja de centrarse tanto en la clase mayoritaria y empieza a clasificar más clientes como positivos. En un problema desbalanceado, esta reducción de exactitud no implica necesariamente que el modelo sea peor; simplemente refleja un cambio en la estrategia de clasificación.

La puntuación F1 de la clase positiva mejora de **0.3172** a **0.4059**. Esto indica que, aunque se pierde precisión, la mejora en sensibilidad compensa parcialmente esa pérdida y produce un mejor equilibrio general para la clase positiva.

### Interpretación comercial

Desde el punto de vista de una campaña de marketing, la elección entre el modelo base y el modelo balanceado depende del coste de contacto y del objetivo comercial.

Si el coste de contactar a un cliente es alto, puede interesar el modelo base, porque selecciona menos clientes, pero con mayor probabilidad de acierto.

Si el coste de contacto es bajo o el objetivo principal es no dejar escapar clientes potenciales, el modelo balanceado puede ser más adecuado, ya que detecta muchos más suscriptores reales, aunque implique contactar también a más clientes que finalmente no contratarán el producto.

Por tanto, el modelo balanceado no sustituye necesariamente al modelo base, sino que representa una estrategia distinta: prioriza la captación de clientes positivos frente a la reducción de falsos positivos.

### Conclusión

El modelo balanceado confirma que el bajo recall del modelo base estaba relacionado con el desbalance de la variable objetivo. Al dar más peso a la clase positiva, el modelo aumenta notablemente su capacidad para detectar suscriptores, pasando de una sensibilidad del **20.31%** a una del **66.56%**.

No obstante, esta mejora se consigue a costa de reducir la precisión y la exactitud global. Por ello, el modelo balanceado resulta especialmente útil en escenarios donde sea preferible detectar más clientes potenciales, incluso si eso implica asumir un mayor número de contactos no convertidos.

## 8. Análisis de umbrales

La regresión logística no devuelve directamente una clase final, sino una **probabilidad estimada** de pertenecer a la clase positiva. En este caso, para cada cliente el modelo estima la probabilidad de que suscriba el producto.

Para transformar esa probabilidad en una predicción final se utiliza un **umbral de decisión**. Por defecto suele emplearse el umbral `0.50`:

- Si la probabilidad estimada es igual o superior a `0.50`, el cliente se clasifica como posible suscriptor.
- Si la probabilidad estimada es inferior a `0.50`, el cliente se clasifica como no suscriptor.

Sin embargo, en problemas de marketing este umbral no tiene por qué ser el más adecuado. Cuando la clase positiva es minoritaria, como ocurre en este proyecto, el umbral `0.50` puede ser demasiado exigente y provocar que el modelo detecte pocos clientes suscriptores.

Por este motivo, se evaluaron distintos umbrales entre `0.20` y `0.50`, analizando cómo cambiaban la exactitud global, la precisión, la sensibilidad y la puntuación F1 de la clase positiva.

### Modelo base

| Umbral | Exactitud global | Precisión clase positiva | Sensibilidad clase positiva | Puntuación F1 clase positiva |
| -----: | ---------------: | -----------------------: | --------------------------: | ---------------------------: |
|   0.20 |           0.8746 |                   0.4485 |                      0.4930 |                       0.4697 |
|   0.25 |           0.8860 |                   0.4932 |                      0.4220 |                       0.4548 |
|   0.30 |           0.8924 |                   0.5317 |                      0.3741 |                       0.4392 |
|   0.35 |           0.8982 |                   0.5830 |                      0.3394 |                       0.4290 |
|   0.40 |           0.9011 |                   0.6267 |                      0.3022 |                       0.4078 |
|   0.45 |           0.9019 |                   0.6726 |                      0.2510 |                       0.3656 |
|   0.50 |           0.9015 |                   0.7235 |                      0.2031 |                       0.3172 |

Los resultados muestran una relación clara entre el umbral utilizado y el comportamiento del modelo.

Con el umbral estándar de `0.50`, el modelo es muy selectivo: solo clasifica como suscriptores a los clientes con una probabilidad estimada relativamente alta. Esto produce una precisión elevada de la clase positiva, del **72.35%**, pero una sensibilidad baja, del **20.31%**. Es decir, cuando el modelo predice que un cliente va a suscribir suele acertar, pero deja sin detectar a la mayoría de los suscriptores reales.

Al reducir el umbral, el modelo clasifica a más clientes como posibles suscriptores. Por ejemplo, con un umbral de `0.20`, la sensibilidad sube hasta el **49.30%**, lo que significa que el modelo detecta casi la mitad de los suscriptores reales. Sin embargo, la precisión baja hasta el **44.85%**, porque al ampliar el grupo de clientes seleccionados también aumentan los falsos positivos.

Este comportamiento refleja el equilibrio habitual entre precisión y sensibilidad:

- Umbrales altos: el modelo selecciona menos clientes, pero con mayor probabilidad de acierto.
- Umbrales bajos: el modelo detecta más clientes potenciales, pero también incluye más clientes que finalmente no suscriben.

La puntuación F1 permite resumir ese equilibrio. En este análisis, el mejor valor de F1 para la clase positiva se obtiene con el umbral `0.20`, alcanzando una puntuación de **0.4697**. Este resultado mejora claramente el F1 obtenido con el umbral estándar de `0.50`, que era **0.3172**.

Desde el punto de vista comercial, esto indica que el umbral de `0.50` puede ser demasiado restrictivo si el objetivo de la campaña es captar más clientes potencialmente interesados. En cambio, un umbral más bajo, como `0.20`, permite detectar un número mayor de posibles suscriptores, aunque implique contactar también a más clientes que finalmente no contratarán el producto.

Por tanto, la elección del umbral debe depender del objetivo de negocio:

- Si el coste de contactar a un cliente es alto, puede ser preferible usar un umbral más elevado, priorizando la precisión.
- Si el coste de contacto es bajo y el objetivo es maximizar la captación, puede ser preferible usar un umbral más bajo, priorizando la sensibilidad.
- Si se busca un equilibrio entre ambas métricas, el umbral `0.20` ofrece el mejor resultado según la puntuación F1 de la clase positiva.

En conclusión, el análisis de umbrales muestra que el rendimiento práctico del modelo puede mejorar sin cambiar el algoritmo, simplemente ajustando el punto de corte utilizado para clasificar a los clientes. Para una campaña comercial orientada a detectar más posibles suscriptores, el umbral `0.20` resulta más adecuado que el umbral estándar de `0.50`.

## 9. Validación cruzada

Además de evaluar el modelo con una única partición entrenamiento-test, se aplicó validación cruzada para comprobar si el rendimiento del modelo era estable al cambiar la división de los datos.

La validación cruzada consiste en dividir el conjunto de datos en varias partes o particiones. En cada iteración, el modelo se entrena con una parte de los datos y se evalúa con otra. De esta forma, se obtiene una visión más robusta del rendimiento, ya que no depende únicamente de una división concreta de entrenamiento y test.

### Resultados obtenidos

| Métrica                |  Media | Desviación típica |
| ---------------------- | -----: | ----------------: |
| Área bajo la curva ROC | 0.6573 |            0.1799 |
| Exactitud global       | 0.8443 |            0.1026 |
| Precisión              | 0.3734 |            0.4352 |
| Sensibilidad           | 0.2188 |            0.3826 |
| Puntuación F1          | 0.1401 |            0.1721 |

Los resultados muestran una variabilidad elevada entre particiones, especialmente en las métricas centradas en la clase positiva. Esto es relevante porque la clase positiva, es decir, los clientes que sí suscriben, representa una proporción pequeña del total de observaciones.

La desviación típica de la precisión, la sensibilidad y la puntuación F1 es elevada. Esto indica que, dependiendo de qué clientes caigan en cada partición de entrenamiento y test, el modelo puede comportarse de forma bastante diferente al detectar suscriptores.

En cambio, la exactitud global es más estable, aunque también presenta cierta variabilidad. No obstante, esta métrica debe interpretarse con cautela porque está influida por el fuerte peso de la clase mayoritaria.

### Interpretación

La validación cruzada indica que el modelo tiene cierta capacidad predictiva, pero también que su rendimiento sobre la clase positiva no es completamente estable. Esto refuerza la necesidad de no evaluar el modelo únicamente con exactitud global y de analizar métricas específicas para la clase de interés.

Desde un punto de vista comercial, esta variabilidad sugiere que el modelo debe utilizarse como herramienta de priorización, no como una regla perfecta de decisión. Es decir, el modelo ayuda a ordenar clientes según su probabilidad de suscripción, pero no garantiza una clasificación exacta en todos los casos.

## 10. Modelo inferencial completo con Statsmodels

Además del modelo predictivo construido con `sklearn`, se estimó una regresión logística con `statsmodels`. El objetivo de este modelo no era solo predecir, sino estudiar la relación estadística entre las variables explicativas y la probabilidad de suscripción.

La regresión logística con `statsmodels` permite analizar coeficientes, errores estándar, valores z, p-valores e intervalos de confianza. Por tanto, resulta más adecuada para la parte inferencial del análisis.

### Resultados principales

| Métrica        |  Valor |
| -------------- | -----: |
| Observaciones  | 43,000 |
| Pseudo R²      | 0.1960 |
| Log-Likelihood | -12170 |
| Df Model       |     37 |
| LLR p-value    |  0.000 |

El modelo completo es globalmente significativo, ya que el p-valor del test de razón de verosimilitud es 0.000. Esto indica que el conjunto de variables incluidas aporta información estadísticamente relevante para explicar la probabilidad de suscripción.

El pseudo R² tiene un valor de 0.1960. En modelos Logit, este indicador no se interpreta igual que el R² de una regresión lineal. No representa el porcentaje exacto de variabilidad explicada, sino una medida aproximada de mejora del modelo respecto a un modelo nulo sin predictores.

### Variables significativas

Algunas variables significativas al 5% fueron:

- `campaign`.
- `nr.employed`.
- `customer_tenure_days`.
- `job_blue-collar`.
- `job_retired`.
- `job_services`.
- `job_student`.
- `education_university.degree`.
- `contact_telephone`.
- `poutcome_nonexistent`.
- `poutcome_success`.

Estas variables presentan evidencia estadística de asociación con la probabilidad de suscripción, manteniendo constantes el resto de variables del modelo.

### Interpretación general

El signo de los coeficientes permite interpretar la dirección de la relación:

- Coeficientes positivos indican que la variable aumenta las odds de suscripción.
- Coeficientes negativos indican que la variable reduce las odds de suscripción.

Por ejemplo, `campaign` tiene un coeficiente negativo, lo que sugiere que un mayor número de contactos durante la campaña está asociado con menor probabilidad de suscripción. Esto puede interpretarse como una señal de saturación: los clientes que requieren más contactos pueden ser menos propensos a contratar.

Por otro lado, variables como `job_retired`, `job_student` y `poutcome_success` presentan coeficientes positivos, lo que indica mayor propensión relativa a la suscripción.

No obstante, este modelo completo incluye muchas variables, algunas de ellas no significativas. Por ese motivo, posteriormente se estimaron modelos reducidos más simples e interpretables.

## 11. Multicolinealidad

Antes de seleccionar el modelo inferencial final, se analizó la posible presencia de multicolinealidad entre variables explicativas.

La multicolinealidad aparece cuando dos o más variables independientes contienen información muy parecida. Esto no siempre perjudica gravemente la predicción, pero sí puede afectar a la interpretación estadística del modelo, ya que vuelve inestables los coeficientes y puede alterar los p-valores.

Para evaluar este problema se utilizaron dos enfoques:

- Matriz de correlación entre variables numéricas.
- Factor de inflación de la varianza, conocido como VIF.

### Resultados principales

| Variable          |      VIF | Interpretación         |
| ----------------- | -------: | ---------------------- |
| `pdays`           | 64086.87 | Multicolinealidad alta |
| `contacto_previo` | 64085.01 | Multicolinealidad alta |

Además, la correlación entre ambas variables fue prácticamente perfecta en valor absoluto:

corr(pdays, contacto_previo) = -0.999992


## 12. Modelos excluyendo `contacto_previo`

Para corregir el problema de multicolinealidad detectado entre `pdays` y `contacto_previo`, se reestimaron los modelos excluyendo `contacto_previo` y manteniendo `pdays`.

Esta decisión se justifica porque `contacto_previo` es una variable derivada de `pdays`, por lo que no aporta información realmente independiente. Mantener ambas variables podía dificultar la interpretación de los coeficientes.

### Modelo inferencial sin `contacto_previo`

| Modelo                         | Pseudo R² | Log-Likelihood | Df Model |
| ------------------------------ | --------: | -------------: | -------: |
| Completo con `contacto_previo` |    0.1960 |         -12170 |       37 |
| Sin `contacto_previo`          |    0.1959 |         -12171 |       36 |

La comparación muestra que eliminar `contacto_previo` apenas reduce la capacidad explicativa del modelo. El pseudo R² pasa de 0.1960 a 0.1959, una diferencia prácticamente inexistente.

Además, al eliminar `contacto_previo`, `pdays` pasa a ser significativa:

| Variable | Coeficiente | P-valor |
| -------- | ----------: | ------: |
| `pdays`  |     -0.0012 |   0.000 |

Esto indica que, una vez eliminada la variable redundante, el efecto de `pdays` puede estimarse con mayor estabilidad.

### Modelo predictivo sin `contacto_previo`

| Métrica                      |  Valor |
| ---------------------------- | -----: |
| Área bajo la curva ROC       | 0.7826 |
| Precisión media              | 0.4544 |
| Exactitud global             | 0.9015 |
| Precisión clase positiva     | 0.7249 |
| Sensibilidad clase positiva  | 0.2023 |
| Puntuación F1 clase positiva | 0.3163 |

El rendimiento predictivo se mantiene prácticamente igual al del modelo con `contacto_previo`. Esto confirma que eliminar esta variable no supone una pérdida relevante de información para la predicción.

### Conclusión

La exclusión de `contacto_previo` mejora la estabilidad inferencial sin perjudicar el rendimiento predictivo. Por tanto, se recomienda no incluir `contacto_previo` en los modelos finales y mantener `pdays` como variable explicativa.

## 13. Modelo Logit reducido sin `contacto_previo`

Después de analizar el modelo completo y detectar multicolinealidad, se estimó un modelo Logit reducido excluyendo `contacto_previo`.

Este modelo se considera el más adecuado para la parte inferencial porque combina tres ventajas:

- Es más simple que el modelo completo.
- Mantiene una capacidad explicativa muy similar.
- Incluye variables estadísticamente significativas.
- Evita el problema de multicolinealidad entre `pdays` y `contacto_previo`.

### Resultados principales

| Métrica        |  Valor |
| -------------- | -----: |
| Observaciones  | 43,000 |
| Pseudo R²      | 0.1950 |
| Log-Likelihood | -12185 |
| Df Model       |     12 |
| LLR p-value    |  0.000 |

El modelo es globalmente significativo, ya que el p-valor del test de razón de verosimilitud es 0.000. Esto indica que las variables incluidas aportan información relevante para explicar la probabilidad de suscripción.

### Comparación con el modelo completo

| Modelo                         | Pseudo R² | Df Model |
| ------------------------------ | --------: | -------: |
| Completo original              |    0.1960 |       37 |
| Reducido sin `contacto_previo` |    0.1950 |       12 |

La pérdida de capacidad explicativa es muy pequeña. El pseudo R² baja de 0.1960 a 0.1950, mientras que el número de variables se reduce de 37 a 12. Esto hace que el modelo reducido sea mucho más interpretable y más fácil de justificar.

### Variables significativas del modelo reducido

Todas las variables incluidas son significativas al 5%:

| Variable                      | Coeficiente | P-valor | Interpretación general                                                |
| ----------------------------- | ----------: | ------: | --------------------------------------------------------------------- |
| `campaign`                    |     -0.0465 |   0.000 | Más contactos en campaña reducen la probabilidad de suscripción.      |
| `pdays`                       |     -0.0011 |   0.000 | Más días desde el contacto anterior reducen la probabilidad.          |
| `nr.employed`                 |     -0.0124 |   0.000 | Mayor nivel de empleo agregado se asocia con menor probabilidad.      |
| `customer_tenure_days`        |      0.0006 |   0.000 | Mayor antigüedad del cliente aumenta la probabilidad.                 |
| `job_blue-collar`             |     -0.2816 |   0.000 | Este perfil reduce las odds frente a la categoría de referencia.      |
| `job_retired`                 |      0.3879 |   0.000 | Los jubilados tienen mayor propensión frente a la referencia.         |
| `job_services`                |     -0.1908 |   0.004 | Este perfil reduce las odds frente a la categoría de referencia.      |
| `job_student`                 |      0.3501 |   0.000 | Los estudiantes tienen mayor propensión frente a la referencia.       |
| `education_university.degree` |      0.1347 |   0.001 | La educación universitaria aumenta la probabilidad.                   |
| `contact_telephone`           |     -0.6889 |   0.000 | El contacto telefónico reduce las odds frente a la referencia.        |
| `poutcome_nonexistent`        |      0.5762 |   0.000 | Ausencia de resultado previo aumenta las odds frente a la referencia. |
| `poutcome_success`            |      0.8063 |   0.000 | Un éxito previo aumenta claramente las odds de suscripción.           |

### Interpretación

El modelo muestra que la probabilidad de suscripción está relacionada con variables de campaña, contexto económico, antigüedad del cliente, ocupación, canal de contacto y resultado de campañas anteriores.

Desde una perspectiva de negocio, destacan tres ideas:

- El historial previo de campaña es relevante.
- El canal de contacto influye en la conversión.
- Un mayor número de contactos durante la campaña no implica necesariamente mayor probabilidad de éxito.

Por tanto, este modelo puede utilizarse para explicar qué factores están asociados con la suscripción, más que para maximizar únicamente la predicción.

## 14. Modelo Logit reducido con errores estándar robustos

Para comprobar la estabilidad del modelo inferencial, se estimó el mismo Logit reducido sin `contacto_previo`, pero utilizando errores estándar robustos HC3.

Los errores estándar robustos permiten obtener inferencias más resistentes ante posibles problemas de heterocedasticidad o especificación del modelo. En este caso, los coeficientes estimados no cambian, pero sí pueden cambiar los errores estándar, los estadísticos z y los p-valores.

### Resultados principales

| Métrica            |  Valor |
| ------------------ | -----: |
| Pseudo R²          | 0.1950 |
| Log-Likelihood     | -12185 |
| Tipo de covarianza |    HC3 |
| LLR p-value        |  0.000 |

El modelo mantiene el mismo ajuste general que el modelo reducido no robusto. Lo relevante es que las variables conservan su significatividad estadística incluso después de aplicar errores estándar robustos.

### Interpretación

Este resultado refuerza la confianza en el modelo inferencial. Si algunas variables hubieran dejado de ser significativas con errores robustos, habría sido necesario interpretar sus efectos con mayor cautela. Sin embargo, en este caso las conclusiones principales se mantienen.

Por tanto, el modelo Logit reducido con errores robustos confirma que los resultados no dependen únicamente de una estimación convencional de los errores estándar.

### Conclusión

El modelo robusto valida la estabilidad de la especificación reducida. Por ello, el modelo Logit reducido sin `contacto_previo`, acompañado de errores estándar robustos HC3, puede considerarse la opción más sólida para la interpretación estadística.

## 15. Odds ratios destacados

En una regresión logística, los coeficientes se expresan en términos de log-odds, lo que puede ser poco intuitivo. Por ello, se calcularon odds ratios, que permiten interpretar los efectos de forma más clara.

El odds ratio se obtiene aplicando la función exponencial al coeficiente:

odds ratio = exp(coeficiente)

Un odds ratio mayor que 1 indica que la variable aumenta las odds de suscripción. Un odds ratio menor que 1 indica que las reduce.

### `poutcome_success`

coeficiente = 0.8063
odds ratio ≈ exp(0.8063) = 2.24
Manteniendo constantes el resto de variables, haber tenido éxito en una campaña anterior multiplica aproximadamente por 2.24 las odds de suscripción frente a la categoría de referencia.

Este es uno de los efectos más relevantes del modelo. Desde una perspectiva comercial, indica que los clientes que respondieron positivamente en campañas anteriores constituyen un segmento especialmente atractivo para futuras acciones.

### `contact_telephone`

coeficiente = -0.6889
odds ratio ≈ exp(-0.6889) = 0.50
Manteniendo constantes el resto de variables, el contacto por teléfono reduce aproximadamente a la mitad las odds de suscripción respecto a la categoría de referencia.

Esto sugiere que el canal de contacto tiene un papel importante en la conversión. Si la categoría de referencia es otro canal, como cellular, el resultado indica que el contacto telefónico tradicional es menos efectivo.

### `campaign`

coeficiente = -0.0465
odds ratio ≈ exp(-0.0465) = 0.95
Cada contacto adicional dentro de la campaña reduce ligeramente las odds de suscripción. Aunque el efecto individual por contacto no es muy grande, sí puede acumularse cuando el número de contactos aumenta.

Este resultado sugiere que insistir demasiado durante una misma campaña puede estar asociado con menor probabilidad de conversión. Desde el punto de vista comercial, puede interpretarse como una señal de fatiga o baja predisposición del cliente.

### Conclusión

Los odds ratios permiten traducir los coeficientes del modelo a una interpretación más útil para negocio. Los resultados muestran que el historial de éxito previo aumenta claramente la propensión a suscribir, mientras que el contacto telefónico y el exceso de contactos durante la campaña se asocian con menor probabilidad de conversión.

Cada contacto adicional dentro de la campaña reduce ligeramente las odds de suscripción. Aunque el efecto individual por contacto no es muy grande, sí puede acumularse cuando el número de contactos aumenta.


## 16. Deciles y lift

Además de evaluar el modelo mediante métricas estadísticas, se construyeron tablas de deciles para analizar su utilidad comercial.

Las tablas de deciles ordenan a los clientes según la probabilidad estimada de suscripción, de mayor a menor, y dividen el conjunto en diez grupos del mismo tamaño. El primer decil contiene el 10% de clientes con mayor probabilidad estimada, mientras que el décimo decil contiene el 10% con menor probabilidad.

Este análisis permite responder a una pregunta clave de negocio:

¿El modelo consigue concentrar a los clientes con mayor probabilidad de conversión en los primeros grupos?

### Modelo completo

| Decil | Clientes | Suscriptores | Tasa de conversión | Lift |
| ----: | -------: | -----------: | -----------------: | ---: |
|     1 |     1075 |          523 |             48.65% | 4.32 |
|     2 |     1075 |          223 |             20.74% | 1.84 |
|     3 |     1075 |           97 |              9.02% | 0.80 |
|    10 |     1075 |           35 |              3.26% | 0.29 |

### Modelo reducido

| Decil | Clientes | Suscriptores | Tasa de conversión | Lift |
| ----: | -------: | -----------: | -----------------: | ---: |
|     1 |     1075 |          528 |             49.12% | 4.36 |
|     2 |     1075 |          216 |             20.09% | 1.78 |
|     3 |     1075 |          101 |              9.40% | 0.83 |
|    10 |     1075 |           35 |              3.26% | 0.29 |

El primer decil concentra una proporción muy elevada de suscriptores. En el modelo reducido, el primer decil alcanza una tasa de conversión del 49.12%, frente a una tasa global aproximada del 11.27%.

El lift de 4.36 significa que contactar a los clientes del primer decil es más de cuatro veces más eficiente que seleccionar clientes aleatoriamente.

Interpretación comercial

Este resultado es uno de los más importantes del proyecto. Aunque el modelo no detecta todos los suscriptores con el umbral estándar de 0.50, sí es muy útil para ordenar clientes por prioridad comercial.

Desde el punto de vista de una campaña, el banco podría utilizar el modelo para seleccionar primero a los clientes del primer decil. Esto permitiría concentrar los esfuerzos comerciales en un grupo con mucha mayor probabilidad de conversión.

Conclusión

Las tablas de deciles muestran que el modelo tiene valor práctico para priorización comercial. El primer decil contiene una concentración muy superior de suscriptores, por lo que el modelo puede utilizarse como herramienta para mejorar la eficiencia de campañas de marketing.

## 17. Modelos sobre el primer decil

Después de comprobar que el primer decil concentraba una tasa de conversión muy superior a la media, se construyó una muestra específica con esos clientes. El objetivo era analizar si, dentro del grupo de mayor propensión, seguían existiendo patrones útiles para diferenciar clientes que suscriben de clientes que no suscriben.

### Características de la muestra

| Métrica                          |  Valor |
| -------------------------------- | -----: |
| Clientes totales                 | 43,000 |
| Clientes en primer decil         |  4,300 |
| Tasa de suscripción total        | 11.27% |
| Tasa de suscripción primer decil | 48.16% |
| Probabilidad media primer decil  | 47.69% |

El primer decil contiene el 10% de clientes con mayor probabilidad estimada. Su tasa de suscripción es del **48.16%**, muy superior a la media total del dataset.

Esto confirma que el modelo es capaz de identificar un segmento de clientes especialmente valioso.

### Modelo inferencial en el primer decil

| Métrica        |     Valor |
| -------------- | --------: |
| Observaciones  |     4,300 |
| Pseudo R²      |    0.0842 |
| Log-Likelihood |   -2727.1 |
| LLR p-value    | 2.793e-83 |

El modelo sigue siendo globalmente significativo, ya que el p-valor del test de razón de verosimilitud es extremadamente bajo. Sin embargo, el pseudo R² es menor que en la muestra completa.

Esta reducción tiene sentido porque el primer decil es una muestra mucho más homogénea. Todos los clientes incluidos tienen una probabilidad estimada relativamente alta, por lo que resulta más difícil explicar diferencias internas.

### Modelo predictivo en el primer decil

| Métrica                      |  Valor |
| ---------------------------- | -----: |
| Área bajo la curva ROC       | 0.6693 |
| Precisión media              | 0.6591 |
| Exactitud global             | 0.6260 |
| Precisión clase positiva     | 0.6343 |
| Sensibilidad clase positiva  | 0.5290 |
| Puntuación F1 clase positiva | 0.5768 |

En el primer decil, el área bajo la curva ROC baja respecto a la muestra total. Esto indica que dentro de este grupo homogéneo el modelo tiene menos capacidad para ordenar clientes.

Sin embargo, la puntuación F1 de la clase positiva mejora notablemente. Esto ocurre porque la proporción de clientes suscriptores es mucho mayor en el primer decil. Por tanto, aunque la discriminación interna sea más difícil, el modelo trabaja sobre una población mucho más favorable.

### Umbrales en el primer decil

| Umbral | Precisión clase positiva | Sensibilidad clase positiva | Puntuación F1 clase positiva |
| -----: | -----------------------: | --------------------------: | ---------------------------: |
|   0.20 |                   0.4853 |                      0.9884 |                       0.6510 |
|   0.25 |                   0.4951 |                      0.9710 |                       0.6558 |
|   0.30 |                   0.5165 |                      0.9073 |                       0.6583 |
|   0.50 |                   0.6343 |                      0.5290 |                       0.5768 |

Dentro del primer decil, el umbral `0.30` ofrece el mejor equilibrio según la puntuación F1. Con este umbral se detecta más del 90% de los suscriptores del primer decil, aunque con una precisión menor que la obtenida con umbral 0.50.

### Conclusión

El primer decil debe interpretarse como un segmento prioritario para campañas comerciales. Dentro de este grupo, la tasa de conversión es muy superior a la media y el ajuste de umbrales permite adaptar la estrategia según el objetivo de negocio.

## 18. Modelos excluyendo el primer decil

También se construyó una muestra excluyendo el primer decil. El objetivo de este análisis era estudiar el comportamiento del modelo en el 90% restante de clientes, es decir, aquellos con menor probabilidad estimada de suscripción.

Este análisis permite responder a otra pregunta de negocio:

¿Qué ocurre si ya hemos contactado al grupo más prometedor y queremos buscar oportunidades en el resto de clientes?

### Características de la muestra

| Métrica                              |  Valor |
| ------------------------------------ | -----: |
| Clientes totales                     | 43,000 |
| Clientes sin primer decil            | 38,700 |
| Clientes eliminados                  |  4,300 |
| Tasa de suscripción total            | 11.27% |
| Tasa de suscripción sin primer decil |  7.17% |

Al eliminar el primer decil, la tasa de suscripción baja del 11.27% al 7.17%. Esto confirma que el primer decil concentra una parte importante de los clientes más valiosos.

### Regresión logística sin primer decil

| Métrica                      |  Valor |
| ---------------------------- | -----: |
| Área bajo la curva ROC       | 0.6668 |
| Precisión media              | 0.1781 |
| Exactitud global             | 0.9284 |
| Precisión clase positiva     | 0.0000 |
| Sensibilidad clase positiva  | 0.0000 |
| Puntuación F1 clase positiva | 0.0000 |

Con umbral 0.50, la regresión logística no identifica ningún positivo en la muestra sin primer decil. La exactitud global es alta, pero engañosa, porque el modelo clasifica todos los casos como no.

Esto ocurre porque, al quitar el primer decil, se elimina el grupo donde el modelo encontraba mayor concentración de clientes propensos. El 90% restante contiene menos positivos y resulta mucho más difícil de clasificar.

### Análisis de umbrales

Con umbrales más bajos, el modelo sí empieza a detectar algunos positivos:

| Umbral | Precisión clase positiva | Sensibilidad clase positiva | Puntuación F1 clase positiva |
| -----: | -----------------------: | --------------------------: | ---------------------------: |
|   0.20 |                   0.3309 |                      0.1284 |                       0.1850 |
|   0.25 |                   0.2941 |                      0.0144 |                       0.0275 |
|   0.30 |                   0.5000 |                      0.0014 |                       0.0029 |

El mejor resultado aparece con umbral 0.20, aunque la sensibilidad sigue siendo baja. Esto muestra que la regresión logística tiene dificultades para encontrar suscriptores fuera del primer decil.

### Conclusión

Excluir el primer decil permite comprobar la robustez del modelo en una población menos favorable. Los resultados indican que el primer decil concentra gran parte de la utilidad comercial del modelo. Una vez eliminado ese grupo, la predicción de suscriptores se vuelve mucho más difícil.

## 19. Comparación con Random Forest

Para comprobar si un modelo más flexible podía mejorar la detección de clientes suscriptores, se comparó la regresión logística sin `contacto_previo` frente a un modelo Random Forest.

Random Forest es un modelo basado en múltiples árboles de decisión. A diferencia de la regresión logística, puede captar relaciones no lineales e interacciones entre variables sin necesidad de especificarlas manualmente.

### Muestra total

| Modelo              | Área bajo la curva ROC | Precisión media | Exactitud global | Precisión clase positiva | Sensibilidad clase positiva | Puntuación F1 clase positiva |
| ------------------- | ---------------------: | --------------: | ---------------: | -----------------------: | --------------------------: | ---------------------------: |
| Regresión logística |                 0.7826 |          0.4544 |           0.9015 |                   0.7249 |                      0.2023 |                       0.3163 |
| Random Forest       |                 0.7953 |          0.4633 |           0.8335 |                   0.3614 |                      0.6235 |                       0.4576 |

En la muestra total, Random Forest mejora el área bajo la curva ROC, la precisión media, la sensibilidad y la puntuación F1 de la clase positiva.

La sensibilidad pasa de **20.23%** en la regresión logística a **62.35%** en Random Forest. Esto significa que Random Forest detecta muchos más clientes que realmente suscriben.

Sin embargo, esta mejora se consigue a costa de una reducción en la precisión de la clase positiva. La precisión baja de **72.49%** a **36.14%**, lo que indica que Random Forest genera más falsos positivos.

### Interpretación comercial

Desde un punto de vista comercial, Random Forest puede ser más útil si el objetivo es detectar más clientes potenciales y el coste de contacto es asumible. En cambio, la regresión logística puede ser preferible si se quiere contactar a menos clientes, pero con mayor probabilidad de acierto.

### Muestra sin primer decil

| Modelo              | Área bajo la curva ROC | Precisión media | Exactitud global | Precisión clase positiva | Sensibilidad clase positiva | Puntuación F1 clase positiva |
| ------------------- | ---------------------: | --------------: | ---------------: | -----------------------: | --------------------------: | ---------------------------: |
| Regresión logística |                 0.6668 |          0.1781 |           0.9284 |                   0.0000 |                      0.0000 |                       0.0000 |
| Random Forest       |                 0.6996 |          0.2165 |           0.7644 |                   0.1546 |                      0.5123 |                       0.2375 |

En la muestra sin primer decil, Random Forest es claramente superior a la regresión logística. La regresión logística no detecta ningún positivo con umbral 0.50, mientras que Random Forest mantiene una sensibilidad del **51.23%**.

Aunque la precisión es baja, Random Forest consigue identificar parte de los suscriptores del grupo más difícil.

### Conclusión

Random Forest mejora la detección de la clase positiva, especialmente cuando se analiza la muestra sin primer decil. Por tanto, puede ser un modelo útil para complementar la regresión logística en escenarios donde el objetivo sea maximizar la captación de posibles suscriptores.

## 20. Validación temporal

Además de la partición aleatoria entrenamiento-test, se realizó una validación temporal. En este enfoque, el modelo se entrena con observaciones más antiguas y se evalúa sobre observaciones más recientes.

Este tipo de validación es especialmente importante en problemas de negocio, ya que se aproxima mejor al uso real del modelo. En una campaña futura, el modelo se entrenaría con datos históricos y se aplicaría sobre nuevos clientes o contactos posteriores.

### Resultados

| Modelo            | Área bajo la curva ROC | Precisión media | Exactitud global | Precisión clase positiva | Sensibilidad clase positiva | Puntuación F1 clase positiva |
| ----------------- | ---------------------: | --------------: | ---------------: | -----------------------: | --------------------------: | ---------------------------: |
| Temporal completo |                 0.7754 |          0.4614 |           0.9014 |                   0.7093 |                      0.2197 |                       0.3354 |
| Temporal reducido |                 0.7755 |          0.4560 |           0.9006 |                   0.7172 |                      0.2031 |                       0.3166 |

Los resultados temporales son similares a los obtenidos con partición aleatoria. El área bajo la curva ROC se mantiene alrededor de 0.775 y la exactitud global permanece cerca del 90%.

Esto indica que el modelo mantiene una capacidad predictiva razonablemente estable cuando se evalúa sobre datos más recientes.

### Interpretación

La validación temporal aporta una comprobación adicional de robustez. Si el rendimiento hubiera caído mucho en esta evaluación, habría indicios de que el modelo dependía demasiado de patrones específicos de periodos anteriores.

En este caso, la estabilidad de las métricas sugiere que el modelo puede generalizar de forma razonable a datos futuros, aunque sigue manteniendo la limitación de baja sensibilidad para la clase positiva con umbral estándar.

### Conclusión

La validación temporal refuerza la utilidad del modelo como herramienta de priorización comercial. El rendimiento no se deteriora de forma importante al pasar de una evaluación aleatoria a una evaluación más cercana al escenario real.

## 21. Tests de normalidad

Se aplicaron tests de normalidad sobre las variables numéricas utilizadas en los modelos de inferencia. Los tests empleados fueron:

- Shapiro-Wilk.
- D'Agostino.
- Jarque-Bera.

Estos tests contrastan si una variable sigue una distribución normal. En todos los casos analizados, tanto en la muestra total como en el primer decil, se rechazó la hipótesis de normalidad.

### Interpretación del resultado

El rechazo de normalidad indica que las variables numéricas no siguen una distribución normal. Esto es habitual en variables como:

- Número de contactos.
- Días desde el contacto anterior.
- Ingresos.
- Variables macroeconómicas.
- Antigüedad del cliente.

Además, con muestras grandes como **43,000 registros**, los tests de normalidad son muy sensibles. Esto significa que pueden rechazar la normalidad incluso cuando las desviaciones no son graves desde un punto de vista práctico.

### Relación con la regresión logística

Este resultado no invalida los modelos Logit estimados. A diferencia de una regresión lineal clásica, la regresión logística no exige normalidad de las variables explicativas ni normalidad de los errores.

Por tanto, los tests de normalidad deben interpretarse como un diagnóstico descriptivo de la distribución de las variables, no como una condición necesaria para validar el modelo.

### Conclusión

Las variables numéricas no siguen una distribución normal, pero esto no supone un problema para la regresión logística. La validez del modelo debe evaluarse mediante su significatividad global, estabilidad de coeficientes, multicolinealidad, capacidad predictiva y utilidad comercial.

## 22. Visualizaciones generadas

Las visualizaciones del proyecto se guardaron en la carpeta `INFORMES/GRAFICOS/`. Estas figuras permiten complementar el análisis estadístico con una interpretación visual de los principales patrones de los datos y del rendimiento de los modelos.

Entre las principales salidas gráficas se incluyen:

- Distribución de la variable objetivo.
- Conversión por canal de contacto.
- Conversión por ocupación.
- Conversión por edad.
- Conversión por mes.
- Conversión por grupo de ingresos.
- Curvas ROC del modelo base y balanceado.
- Curvas precisión-sensibilidad del modelo base y balanceado.
- Curvas ROC y precisión-sensibilidad del modelo reducido.

### Utilidad de las visualizaciones

Las visualizaciones descriptivas permiten identificar diferencias de conversión entre grupos de clientes. Por ejemplo, ayudan a comparar tasas de suscripción según ocupación, canal de contacto, edad o grupo de ingresos.

Las curvas ROC permiten evaluar la capacidad general del modelo para ordenar correctamente clientes suscriptores y no suscriptores. Cuanto más se aleja la curva de la diagonal aleatoria, mayor es la capacidad discriminante del modelo.

Las curvas precisión-sensibilidad son especialmente importantes en este proyecto porque la variable objetivo está desbalanceada. Estas curvas permiten analizar mejor el comportamiento del modelo sobre la clase positiva, que es la clase de mayor interés comercial.

### Conclusión

Las visualizaciones generadas ayudan a interpretar tanto el comportamiento de los datos como el rendimiento de los modelos. En conjunto, complementan las tablas de resultados y facilitan la comunicación de los hallazgos principales del proyecto.

## 23. Conclusiones finales

1. La tasa global de suscripción es baja, aproximadamente **11.27%**, por lo que el problema está claramente desbalanceado.
2. El modelo inicial tiene buena accuracy, pero bajo recall de la clase positiva.
3. Bajar el umbral de clasificación mejora la detección de suscriptores. En el modelo base, el umbral `0.20` ofrece el mejor F1-score entre los umbrales analizados.
4. El análisis de multicolinealidad detecta una relación casi perfecta entre `pdays` y `contacto_previo`, por lo que no deben incluirse simultáneamente en modelos inferenciales.
5. El modelo Logit reducido sin `contacto_previo` es el modelo inferencial más recomendable: conserva casi todo el ajuste del modelo completo, pero con muchas menos variables y sin el problema de multicolinealidad principal.
6. La estimación con errores estándar robustos confirma la estabilidad de las conclusiones inferenciales.
7. Las tablas de deciles muestran que el modelo es muy útil comercialmente: el primer decil alcanza una tasa de conversión cercana al **49%**, frente al **11.27%** de la muestra total.
8. Al eliminar el primer decil, la tasa de suscripción baja al **7.17%**, lo que confirma que el primer decil concentra clientes de alto valor.
9. Random Forest mejora la detección de clientes suscriptores frente a la regresión logística, especialmente en términos de recall y F1-score de la clase positiva.
10. Para priorización comercial, se recomienda contactar primero a los clientes del primer decil y, para el resto de clientes, considerar modelos más flexibles como Random Forest.

## 24. Recomendación de modelos

| Objetivo                  | Modelo recomendado                                             |
| ------------------------- | -------------------------------------------------------------- |
| Inferencia estadística    | Logit reducido sin `contacto_previo`                           |
| Inferencia robusta        | Logit reducido sin `contacto_previo` con errores estándar HC3  |
| Predicción interpretable  | Regresión logística sin `contacto_previo` con ajuste de umbral |
| Captar más suscriptores   | Random Forest                                                  |
| Priorización comercial    | Tabla de deciles / lift                                        |
| Análisis del 90% restante | Random Forest sin primer decil                                 |

## 25. Recomendación de negocio

Desde un punto de vista comercial, el banco debería utilizar el modelo como herramienta de priorización, no como una regla automática de decisión.

La estrategia recomendada sería:

1. Priorizar el primer decil de clientes, donde la tasa de conversión supera ampliamente la media global.
2. Usar un umbral inferior a `0.50` si el objetivo es maximizar la captación de suscriptores.
3. Evitar insistir excesivamente en clientes con baja probabilidad de conversión, ya que `campaign` tiene efecto negativo.
4. Dar especial importancia al historial de campañas anteriores, especialmente cuando `poutcome = success`.
5. Revisar el canal de contacto, ya que `contact_telephone` aparece asociado con menor probabilidad de suscripción.
6. Para clientes fuera del primer decil, utilizar modelos más flexibles como Random Forest, ya que la regresión logística pierde capacidad de detección.

## 26. Principales recomendaciones

Si el banco quisiera maximizar la cantidad de suscripciones de la campaña, debería concentrar sus esfuerzos en los clientes con mayor probabilidad estimada de contratación.

Para ello, no se recomienda seleccionar clientes únicamente por una característica aislada, como la renta, la edad o la ocupación. La recomendación principal es utilizar el modelo predictivo como herramienta de scoring, de forma que cada cliente reciba una probabilidad estimada de suscripción a partir de la combinación de sus variables.

Según los resultados del análisis, los clientes con mayor propensión suelen presentar algunas de las siguientes características:

- Pertenecer al primer decil de probabilidad estimada por el modelo.
- Haber tenido un buen resultado en campañas anteriores.
- Ser contactables por un canal distinto al teléfono tradicional.
- Tener ocupaciones como jubilado o estudiante.
- Tener estudios universitarios.
- Tener mayor antigüedad como clientes.
- Haber requerido pocos contactos durante la campaña actual.
- Haber pasado menos tiempo desde el contacto anterior.

No obstante, estas características no deben utilizarse como una regla manual rígida. Un cliente puede no cumplir todas ellas y aun así tener una probabilidad alta, o puede cumplir alguna característica favorable pero quedar penalizado por otras variables. Por ello, la decisión debe basarse en la probabilidad final calculada por el modelo.

El flujo real de trabajo recomendado sería:

1. Se incorporan nuevos clientes o nuevos contactos potenciales.
2. Se recogen las variables necesarias para el modelo, como `job`, `education`, `contact`, `campaign`, `pdays`, `nr.employed`, `customer_tenure_days` y `poutcome`.
3. El modelo elegido calcula una probabilidad estimada de suscripción para cada cliente.
4. Los clientes se ordenan de mayor a menor probabilidad estimada.
5. Se dividen en deciles de probabilidad.
6. Se contacta primero con los clientes del primer decil, es decir, el 10% con mayor probabilidad estimada.
7. Si hay capacidad comercial adicional, se continúa con el segundo decil y se evalúa progresivamente el rendimiento de los siguientes grupos.

Desde el punto de vista comercial, este enfoque permite priorizar los recursos de la campaña hacia los clientes con mayor propensión estimada, aumentando la eficiencia del contacto y reduciendo la selección aleatoria de clientes.


## 27. Limitaciones del análisis

Aunque el proyecto ofrece una visión completa del comportamiento de las campañas bancarias y de la probabilidad de suscripción, los resultados deben interpretarse teniendo en cuenta varias limitaciones:

1. **Los datos son históricos.** El modelo aprende patrones de campañas anteriores, pero el comportamiento de clientes futuros puede cambiar por nuevas condiciones económicas, cambios comerciales o modificaciones en la estrategia de contacto.
2. **El modelo prioriza clientes, no garantiza conversiones.** Las probabilidades estimadas deben usarse como herramienta de ordenación y apoyo a la decisión, no como una regla automática e infalible.
3. **La variable `duration` no debe usarse para predicción previa al contacto.** Aunque es muy informativa, se conoce después de realizar la llamada. Por eso se excluyó de los modelos predictivos para evitar fuga de información.
4. **La selección de variables es exploratoria.** Las variables significativas del modelo Logit reducido ayudan a interpretar patrones, pero deberían validarse con nuevos datos antes de tomar decisiones definitivas.
5. **Existe desbalance en la variable objetivo.** La tasa de suscripción es baja, por lo que métricas como la exactitud global pueden ser engañosas. Por este motivo se analizaron precisión, sensibilidad, F1, ROC AUC, average precision y deciles.
6. **Los deciles deben validarse fuera de muestra.** La versión revisada del código calcula deciles a partir de predicciones sobre test, lo que ofrece una evaluación más realista que calcularlos sobre los mismos datos usados para entrenar.
7. **No se ha incorporado una matriz económica de costes y beneficios.** Para una aplicación real, sería recomendable incluir el coste de contacto, el beneficio esperado por suscripción y la capacidad comercial disponible.
8. **Random Forest mejora la detección de positivos, pero reduce interpretabilidad.** Puede ser útil para priorización, pero la regresión logística sigue siendo más clara para explicar relaciones entre variables y suscripción.

En consecuencia, el análisis debe entenderse como una base sólida para priorización comercial y aprendizaje del comportamiento de los clientes, pero no como una solución final cerrada para producción sin validación adicional.

## 28. Futuras aplicaciones y líneas de mejora

Como futura aplicación de machine learning o inteligencia artificial, el banco podría convertir este análisis en un sistema de scoring comercial que calcule automáticamente la probabilidad de suscripción de nuevos clientes, actualice los deciles antes de cada campaña y recomiende qué clientes contactar primero según la probabilidad estimada, el coste de contacto y el beneficio esperado.

Otras mejoras futuras serían:

- Incorporar calibración de probabilidades para que las probabilidades estimadas sean más fiables.
- Comparar más modelos, como Gradient Boosting, XGBoost, LightGBM o CatBoost.
- Crear una matriz coste-beneficio para elegir el umbral óptimo desde el punto de vista económico.
- Usar validación temporal continua para comprobar si el modelo se degrada con el tiempo.
- Desplegar el modelo en una aplicación interna donde el equipo comercial pueda cargar nuevos clientes y obtener un ranking de prioridad.
- Monitorizar sesgos o diferencias de rendimiento entre segmentos de clientes.
- Automatizar la generación de informes después de cada nueva campaña.

## 29. Cómo ejecutar el proyecto


Instala las dependencias:

```bash
pip install -r requirements.txt
```

Ejecuta el análisis:

```bash
python CODIGO/marketing_bancos.py
```

Al finalizar, se generan:

- Datasets limpios en `DATOS/PROCESADOS/`.
- Tablas resumen en `INFORMES/tablas_resumen_eda.xlsx`.
- Gráficos en `INFORMES/GRAFICOS/`.
- Resultados impresos por consola o guardados en `resultados_regresiones.txt`.
