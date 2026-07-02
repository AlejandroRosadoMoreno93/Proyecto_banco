"""Punto de entrada del proyecto modular."""
import warnings

from config import FEATURES_LOGIT_REDUCIDO, FEATURES_SIN_CONTACTO_PREVIO, DUMMY_COLS_LOGIT_REDUCIDO, PROCESSED, FIG, REPORTS
from data_preparation import preparar_dataset
from eda import generar_graficos
from excel_export import crear_excel_final_limpio
from modeling import (
    ajustar_logit,
    analizar_multicolinealidad,
    entrenar_modelos_predictivos,
    interpretar_odds_ratios,
    test_normalidad,
    validacion_temporal,
)
from utils import crear_directorios

warnings.filterwarnings("ignore")


def main() -> None:
    """Ejecuta el flujo completo del proyecto."""
    crear_directorios()

    # 1. Carga, limpieza y unión
    _, _, merged = preparar_dataset()

    # 2. EDA visual
    generar_graficos(merged)

    # 3. Modelos predictivos principales
    resultados_predictivos = entrenar_modelos_predictivos(merged)

    # 4. Modelo inferencial final recomendado
    logit_final = ajustar_logit(
        merged,
        nombre="logit_reducido_sin_contacto_previo",
        features=FEATURES_LOGIT_REDUCIDO,
        columnas_dummies=DUMMY_COLS_LOGIT_REDUCIDO,
        robusto=False,
    )

    logit_robusto = ajustar_logit(
        merged,
        nombre="logit_reducido_sin_contacto_previo_robusto_HC3",
        features=FEATURES_LOGIT_REDUCIDO,
        columnas_dummies=DUMMY_COLS_LOGIT_REDUCIDO,
        robusto=True,
    )

    # 5. Diagnósticos
    correlacion, vif = analizar_multicolinealidad(merged)
    odds = interpretar_odds_ratios(logit_final["tabla"])
    normalidad = test_normalidad(merged, nombre_muestra="muestra_total")

    # 6. Validación temporal
    validacion_temp = validacion_temporal(
        merged,
        FEATURES_SIN_CONTACTO_PREVIO,
        nombre_modelo="logistica_validacion_temporal",
    )

    # 7. Exportación con formato: índice, hojas agrupadas y estilos
    crear_excel_final_limpio(
        merged=merged,
        resultados_predictivos=resultados_predictivos,
        logit_final=logit_final,
        logit_robusto=logit_robusto,
        correlacion=correlacion,
        vif=vif,
        odds=odds,
        validacion_temp=validacion_temp,
        normalidad=normalidad,
    )

    print("Proceso completado correctamente.")
    print("Datasets limpios guardados en:", PROCESSED)
    print("Gráficos guardados en:", FIG)
    print("Excel final limpio guardado en:", REPORTS / "resultados_modelos_finales.xlsx")


if __name__ == "__main__":
    main()
