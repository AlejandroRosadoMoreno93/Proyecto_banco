"""Configuración central del proyecto de marketing bancario."""
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "DATOS" / "BRUTOS"
PROCESSED = BASE / "DATOS" / "PROCESADOS"
REPORTS = BASE / "INFORMES"
FIG = REPORTS / "GRAFICOS"

BANK_FILE = RAW / "bank-additional.csv"
CUSTOMERS_FILE = RAW / "customer-details.xlsx"

RANDOM_STATE = 42
TEST_SIZE = 0.25
THRESHOLDS = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]

MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}

DECIMAL_COLS_BANK = ["cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed"]
CUSTOMER_NUMERIC_COLS = ["Income", "Kidhome", "Teenhome", "NumWebVisitsMonth"]
CONVERSION_COLS = ["job", "education", "marital", "contact", "poutcome", "income_group", "age_group"]

FEATURES_COMPLETO = [
    "age", "job", "marital", "education", "contact", "campaign", "pdays", "previous",
    "poutcome", "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed",
    "contacto_previo", "Income", "total_children_home", "customer_tenure_days", "income_group",
]

FEATURES_SIN_CONTACTO_PREVIO = [col for col in FEATURES_COMPLETO if col != "contacto_previo"]

FEATURES_LOGIT_REDUCIDO = [
    "campaign", "pdays", "nr.employed", "customer_tenure_days", "job", "education", "contact", "poutcome",
]

DUMMY_COLS_LOGIT_REDUCIDO = [
    "campaign", "pdays", "nr.employed", "customer_tenure_days", "job_blue-collar",
    "job_retired", "job_services", "job_student", "education_university.degree",
    "contact_telephone", "poutcome_nonexistent", "poutcome_success",
]

VIF_NUMERIC_COLS = [
    "age", "campaign", "pdays", "previous", "cons.price.idx", "cons.conf.idx", "euribor3m",
    "nr.employed", "contacto_previo", "Income", "total_children_home", "customer_tenure_days",
]
