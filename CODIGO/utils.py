"""Funciones auxiliares reutilizables."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from config import RAW, PROCESSED, REPORTS, FIG, MESES


def crear_directorios() -> None:
    """Crea las carpetas de salida si no existen."""
    for path in [RAW, PROCESSED, REPORTS, FIG]:
        path.mkdir(parents=True, exist_ok=True)

def columnas_existentes(df: pd.DataFrame, columnas: list[str]) -> list[str]:
    """Devuelve solo las columnas que existen en el DataFrame."""
    return [col for col in columnas if col in df.columns]

def eliminar_columnas_unnamed(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina columnas residuales tipo Unnamed."""
    return df.drop(columns=[c for c in df.columns if str(c).startswith("Unnamed")], errors="ignore")

def parsear_fecha_espanol(valor) -> pd.Timestamp:
    """Convierte fechas tipo '12-mayo-2013' en fechas de pandas."""
    if pd.isna(valor):
        return pd.NaT

    partes = str(valor).strip().lower().split("-")
    if len(partes) != 3:
        return pd.NaT

    dia, mes, anio = partes
    try:
        return pd.Timestamp(year=int(anio), month=MESES[mes], day=int(dia))
    except Exception:
        return pd.NaT

def convertir_decimal(serie: pd.Series) -> pd.Series:
    """Convierte números escritos con coma decimal a formato numérico."""
    return pd.to_numeric(
        serie.astype(str).str.replace(",", ".", regex=False).replace({"nan": np.nan}),
        errors="coerce",
    )

def guardar_grafico(nombre: str) -> None:
    """Guarda el gráfico actual y lo cierra."""
    plt.tight_layout()
    plt.savefig(FIG / nombre, dpi=160, bbox_inches="tight")
    plt.close()
