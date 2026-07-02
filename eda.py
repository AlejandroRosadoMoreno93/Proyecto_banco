"""Análisis exploratorio y visualizaciones."""
import pandas as pd
import matplotlib.pyplot as plt
from config import CONVERSION_COLS
from utils import guardar_grafico


def tabla_conversion(df: pd.DataFrame, col: str, min_n: int = 0) -> pd.DataFrame:
    """Calcula clientes y tasa de conversión por grupo."""
    tabla = (
        df.groupby(col, dropna=False)
        .agg(
            clientes=("subscribed", "size"),
            conversion_pct=("subscribed", lambda x: x.mean() * 100),
        )
        .reset_index()
        .sort_values("conversion_pct", ascending=False)
    )
    return tabla[tabla["clientes"] >= min_n]

def generar_graficos(df: pd.DataFrame) -> None:
    """Genera los gráficos principales del EDA."""
    df["y"].value_counts().reindex(["no", "yes"]).plot(
        kind="bar", title="Distribución de la variable objetivo"
    )
    plt.xlabel("Resultado")
    plt.ylabel("Clientes")
    guardar_grafico("01_distribucion_objetivo.png")

    tabla_conversion(df, "contact").set_index("contact")["conversion_pct"].plot(
        kind="bar", title="Conversión por contacto"
    )
    plt.xlabel("Contacto")
    plt.ylabel("Conversión (%)")
    guardar_grafico("02_conversion_por_contacto.png")

    tabla_conversion(df, "job", min_n=200).sort_values("conversion_pct").set_index("job")["conversion_pct"].plot(
        kind="barh", title="Conversión por ocupación"
    )
    plt.xlabel("Conversión (%)")
    plt.ylabel("Ocupación")
    guardar_grafico("03_conversion_por_ocupacion.png")

    df.boxplot(column="age", by="y")
    plt.suptitle("")
    plt.title("Edad por resultado")
    plt.xlabel("Resultado")
    plt.ylabel("Edad")
    guardar_grafico("04_edad_por_resultado.png")

    (df.groupby("contact_month")["subscribed"].mean() * 100).plot(
        kind="line", marker="o", title="Conversión por mes"
    )
    plt.xlabel("Mes")
    plt.ylabel("Conversión (%)")
    guardar_grafico("05_conversion_por_mes.png")

    tabla_conversion(df, "income_group").set_index("income_group")["conversion_pct"].plot(
        kind="bar", title="Conversión por ingresos"
    )
    plt.xlabel("Grupo de ingresos")
    plt.ylabel("Conversión (%)")
    guardar_grafico("06_conversion_por_ingresos.png")