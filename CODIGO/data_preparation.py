"""Carga, limpieza y unión de datos."""
import numpy as np
import pandas as pd
from config import BANK_FILE, CUSTOMERS_FILE, DECIMAL_COLS_BANK, CUSTOMER_NUMERIC_COLS, PROCESSED
from utils import columnas_existentes, convertir_decimal, eliminar_columnas_unnamed, parsear_fecha_espanol


def cargar_datos() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Carga el CSV bancario y concatena todas las hojas del Excel de clientes."""
    bank = pd.read_csv(BANK_FILE)
    hojas_excel = pd.read_excel(CUSTOMERS_FILE, sheet_name=None)

    customers = []
    for nombre_hoja, df_hoja in hojas_excel.items():
        df_temp = df_hoja.copy()
        df_temp["customer_sheet_year"] = int(nombre_hoja)
        customers.append(df_temp)

    return bank, pd.concat(customers, ignore_index=True)

def limpiar_bank(bank_raw: pd.DataFrame) -> pd.DataFrame:
    """Limpia y transforma el dataset bancario."""
    bank = eliminar_columnas_unnamed(bank_raw.copy())

    for col in columnas_existentes(bank, DECIMAL_COLS_BANK):
        bank[col] = convertir_decimal(bank[col])

    bank["date_parsed"] = bank["date"].apply(parsear_fecha_espanol)
    bank["contact_month"] = bank["date_parsed"].dt.month
    bank["contact_year"] = bank["date_parsed"].dt.year
    bank["subscribed"] = bank["y"].map({"yes": 1, "no": 0})

    text_cols = bank.select_dtypes(include="object").columns
    for col in text_cols:
        if col not in ["id_", "date"]:
            bank[col] = bank[col].fillna("desconocido").astype(str).str.strip().str.lower()

    for col in bank.select_dtypes(include=[np.number]).columns:
        if col != "subscribed" and bank[col].isna().any():
            bank[f"{col}_missing"] = bank[col].isna().astype(int)
            bank[col] = bank[col].fillna(bank[col].median())

    bank["contacto_previo"] = np.where(bank["pdays"].eq(999), 0, 1)
    bank["age_group"] = pd.cut(
        bank["age"],
        bins=[0, 29, 39, 49, 59, 200],
        labels=["<30", "30-39", "40-49", "50-59", "60+"],
    )
    bank["duration_min"] = bank["duration"] / 60

    return bank

def limpiar_customers(customers_raw: pd.DataFrame, ref_date: pd.Timestamp) -> pd.DataFrame:
    """Limpia y transforma el dataset de clientes."""
    customers = eliminar_columnas_unnamed(customers_raw.copy())
    customers = customers.rename(columns={"ID": "id_", "Dt_Customer": "customer_since"})
    customers["customer_since"] = pd.to_datetime(customers["customer_since"], errors="coerce")

    for col in columnas_existentes(customers, CUSTOMER_NUMERIC_COLS):
        customers[col] = pd.to_numeric(customers[col], errors="coerce")
        if customers[col].isna().any():
            customers[f"{col}_missing"] = customers[col].isna().astype(int)
            customers[col] = customers[col].fillna(customers[col].median())

    customers["total_children_home"] = customers["Kidhome"] + customers["Teenhome"]
    customers["customer_tenure_days"] = (ref_date - customers["customer_since"]).dt.days
    customers["income_group"] = pd.qcut(
        customers["Income"],
        q=4,
        labels=["Q1 bajo", "Q2 medio-bajo", "Q3 medio-alto", "Q4 alto"],
        duplicates="drop",
    )

    return customers

def preparar_dataset() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Carga, limpia, une y guarda los datasets principales."""
    bank_raw, customers_raw = cargar_datos()
    bank = limpiar_bank(bank_raw)

    ref_date = max(
        bank["date_parsed"].max(),
        pd.to_datetime(customers_raw["Dt_Customer"], errors="coerce").max(),
    )

    customers = limpiar_customers(customers_raw, ref_date)
    merged = bank.merge(customers, on="id_", how="left", validate="one_to_one")

    bank.to_csv(PROCESSED / "bank_marketing_limpio.csv", index=False)
    customers.to_csv(PROCESSED / "customer_details_limpio.csv", index=False)
    merged.to_csv(PROCESSED / "bank_customer_merged_limpio.csv", index=False)

    return bank, customers, merged
