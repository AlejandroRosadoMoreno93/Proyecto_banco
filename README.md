# Proyecto EDA y modelización con Python: campañas de marketing bancario

Este repositorio contiene una versión modular y limpia del análisis de campañas de marketing bancario.

## Estructura principal

```text
PROYECTO_MARKETING_BANCO/
├── CODIGO/
│   ├── config.py              # rutas, constantes y listas de variables
│   ├── utils.py               # utilidades comunes
│   ├── data_preparation.py    # carga, limpieza y unión de datasets
│   ├── eda.py                 # tablas de conversión y gráficos
│   ├── modeling.py            # modelos, métricas, deciles y validaciones
│   ├── excel_export.py        # Excel final con índice, hojas agrupadas y formato
│   ├── main.py                # flujo principal
│   └── marketing_bancos.py    # wrapper para mantener el comando original
├── DATOS/
│   ├── BRUTOS/
│   └── PROCESADOS/
├── INFORMES/
│   ├── informe_modelizacion_banco.md
│   ├── resultados_modelos_finales.xlsx
│   └── GRAFICOS/
└── requirements.txt
```

## Ejecución

Instalar dependencias:

```
pip install -r requirements.txt
```

Ejecutar el proyecto:

```
python CODIGO/marketing_bancos.py
```

El Excel final se genera en:

```
INFORMES/resultados_modelos_finales.xlsx
```

El exportador conserva índice de navegación, títulos, filtros, formatos de porcentaje, bordes y tablas agrupadas por hoja.
