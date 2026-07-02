"""Modelización predictiva, inferencial y validación."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy.stats import jarque_bera, kurtosis, normaltest, shapiro, skew
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, classification_report, confusion_matrix, PrecisionRecallDisplay, RocCurveDisplay, roc_auc_score
from sklearn.model_selection import cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from statsmodels.stats.outliers_influence import variance_inflation_factor
from config import RANDOM_STATE, TEST_SIZE, THRESHOLDS, FEATURES_SIN_CONTACTO_PREVIO, VIF_NUMERIC_COLS, FIG
from utils import columnas_existentes, guardar_grafico


def preparar_xy(df: pd.DataFrame, features: list[str]) -> tuple[pd.DataFrame, pd.Series]:
    """Prepara matriz de variables explicativas y variable objetivo."""
    features_validas = columnas_existentes(df, features)
    X = df[features_validas].copy()
    y = df["subscribed"].copy()

    mask = y.notna()
    return X.loc[mask], y.loc[mask].astype(int)

def crear_preprocesador(X: pd.DataFrame) -> ColumnTransformer:
    """Crea preprocesador con imputación, escalado y one-hot encoding."""
    numericas = X.select_dtypes(include=[np.number]).columns.tolist()
    categoricas = X.select_dtypes(include=["object", "category"]).columns.tolist()

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numericas),
            ("cat", categorical_pipeline, categoricas),
        ]
    )

def crear_modelo_logistico(X: pd.DataFrame, class_weight=None) -> Pipeline:
    """Crea un pipeline de regresión logística."""
    return Pipeline(
        steps=[
            ("preprocessor", crear_preprocesador(X)),
            ("model", LogisticRegression(max_iter=1000, class_weight=class_weight)),
        ]
    )

def crear_modelo_random_forest(X: pd.DataFrame) -> Pipeline:
    """Crea un pipeline de Random Forest."""
    return Pipeline(
        steps=[
            ("preprocessor", crear_preprocesador(X)),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=300,
                    max_depth=8,
                    min_samples_leaf=50,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                ),
            ),
        ]
    )

def evaluar_modelo(nombre: str, modelo: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict[str, pd.DataFrame]:
    """Evalúa un modelo ya entrenado y devuelve métricas principales."""
    y_pred = modelo.predict(X_test)
    y_proba = modelo.predict_proba(X_test)[:, 1]

    informe = pd.DataFrame(
        classification_report(y_test, y_pred, labels=[0, 1], output_dict=True, zero_division=0)
    ).transpose()

    matriz = pd.DataFrame(
        confusion_matrix(y_test, y_pred, labels=[0, 1]),
        index=["Real no", "Real yes"],
        columns=["Predicho no", "Predicho yes"],
    )

    metricas = pd.DataFrame(
        {
            "modelo": [nombre],
            "roc_auc": [roc_auc_score(y_test, y_proba)],
            "average_precision": [average_precision_score(y_test, y_proba)],
            "accuracy": [informe.loc["accuracy", "precision"]],
            "precision_clase_1": [informe.loc["1", "precision"]],
            "recall_clase_1": [informe.loc["1", "recall"]],
            "f1_clase_1": [informe.loc["1", "f1-score"]],
        }
    )

    return {"metricas": metricas, "matriz": matriz, "informe": informe, "probabilidades": y_proba}

def tabla_umbrales(y_true: pd.Series, y_proba: np.ndarray, thresholds: list[float] = THRESHOLDS) -> pd.DataFrame:
    """Evalúa distintos umbrales de clasificación."""
    resultados = []

    for umbral in thresholds:
        y_pred = (y_proba >= umbral).astype(int)
        informe = classification_report(y_true, y_pred, labels=[0, 1], output_dict=True, zero_division=0)
        matriz = confusion_matrix(y_true, y_pred, labels=[0, 1])

        resultados.append(
            {
                "umbral": umbral,
                "accuracy": informe["accuracy"],
                "precision_clase_1": informe["1"]["precision"],
                "recall_clase_1": informe["1"]["recall"],
                "f1_clase_1": informe["1"]["f1-score"],
                "falsos_positivos": matriz[0, 1],
                "falsos_negativos": matriz[1, 0],
                "verdaderos_positivos": matriz[1, 1],
                "verdaderos_negativos": matriz[0, 0],
            }
        )

    return pd.DataFrame(resultados)

def entrenar_modelos_predictivos(df: pd.DataFrame) -> dict[str, object]:
    """Entrena modelos principales y compara sus métricas."""
    X, y = preparar_xy(df, FEATURES_SIN_CONTACTO_PREVIO)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    modelos = {
        "logistica_base": crear_modelo_logistico(X),
        "logistica_balanceada": crear_modelo_logistico(X, class_weight="balanced"),
        "random_forest": crear_modelo_random_forest(X),
    }

    evaluaciones = {}
    for nombre, modelo in modelos.items():
        modelo.fit(X_train, y_train)
        evaluaciones[nombre] = evaluar_modelo(nombre, modelo, X_test, y_test)

    comparacion = pd.concat([ev["metricas"] for ev in evaluaciones.values()], ignore_index=True)
    umbrales_base = tabla_umbrales(y_test, evaluaciones["logistica_base"]["probabilidades"])
    umbrales_balanceado = tabla_umbrales(y_test, evaluaciones["logistica_balanceada"]["probabilidades"])
    deciles_base = tabla_deciles_desde_probabilidades(y_test, evaluaciones["logistica_base"]["probabilidades"], "logistica_base_test")
    deciles_balanceado = tabla_deciles_desde_probabilidades(y_test, evaluaciones["logistica_balanceada"]["probabilidades"], "logistica_balanceada_test")

    RocCurveDisplay.from_estimator(modelos["logistica_base"], X_test, y_test)
    plt.title("Curva ROC - Regresión logística base")
    guardar_grafico("07_curva_roc_logistica_base.png")

    PrecisionRecallDisplay.from_estimator(modelos["logistica_base"], X_test, y_test)
    plt.title("Curva Precision-Recall - Regresión logística base")
    guardar_grafico("08_curva_precision_recall_logistica_base.png")

    cv = cross_validate(
        crear_modelo_logistico(X),
        X,
        y,
        cv=5,
        scoring={"roc_auc": "roc_auc", "accuracy": "accuracy", "precision": "precision", "recall": "recall", "f1": "f1"},
    )
    cv_df = pd.DataFrame(cv)
    cv_resumen = pd.DataFrame(
        {
            "metrica": ["roc_auc", "accuracy", "precision", "recall", "f1"],
            "media": [cv_df[f"test_{m}"].mean() for m in ["roc_auc", "accuracy", "precision", "recall", "f1"]],
            "desviacion_tipica": [cv_df[f"test_{m}"].std() for m in ["roc_auc", "accuracy", "precision", "recall", "f1"]],
        }
    )

    return {
        "modelos": modelos,
        "evaluaciones": evaluaciones,
        "comparacion": comparacion,
        "umbrales_base": umbrales_base,
        "umbrales_balanceado": umbrales_balanceado,
        "deciles_base": deciles_base,
        "deciles_balanceado": deciles_balanceado,
        "cv_detalle": cv_df,
        "cv_resumen": cv_resumen,
    }

def preparar_xy_logit(df: pd.DataFrame, features: list[str], columnas_dummies: list[str] | None = None) -> tuple[pd.DataFrame, pd.Series]:
    """Prepara variables para modelos Logit de statsmodels."""
    X, y = preparar_xy(df, features)
    X = pd.get_dummies(X, drop_first=True)
    X = X.apply(pd.to_numeric, errors="coerce")

    if columnas_dummies is not None:
        columnas_validas = columnas_existentes(X, columnas_dummies)
        X = X[columnas_validas].copy()

    data_modelo = pd.concat([y, X], axis=1).dropna()
    y_modelo = data_modelo["subscribed"].astype(float)
    X_modelo = data_modelo.drop(columns="subscribed").astype(float)

    return sm.add_constant(X_modelo), y_modelo

def ajustar_logit(
    df: pd.DataFrame,
    nombre: str,
    features: list[str],
    columnas_dummies: list[str] | None = None,
    robusto: bool = False,
) -> dict[str, object]:
    """Ajusta un modelo Logit y devuelve coeficientes, odds ratios y resumen."""
    X_modelo, y_modelo = preparar_xy_logit(df, features, columnas_dummies)
    modelo = sm.Logit(y_modelo, X_modelo)

    resultado = modelo.fit(maxiter=1000, cov_type="HC3") if robusto else modelo.fit(maxiter=1000)
    tabla = resultado.summary2().tables[1].copy()
    tabla["odds_ratio"] = np.exp(tabla["Coef."])
    tabla["or_ci_2.5%"] = np.exp(tabla["[0.025"])
    tabla["or_ci_97.5%"] = np.exp(tabla["0.975]"])
    tabla = tabla.reset_index().rename(columns={"index": "variable"})

    resumen = pd.DataFrame(
        {
            "elemento": ["modelo", "observaciones", "pseudo_r2", "log_likelihood", "aic", "bic", "cov_type", "variables_usadas"],
            "valor": [
                nombre,
                int(resultado.nobs),
                resultado.prsquared,
                resultado.llf,
                resultado.aic,
                resultado.bic,
                "HC3" if robusto else "convencional",
                ", ".join(X_modelo.drop(columns="const", errors="ignore").columns),
            ],
        }
    )

    return {"resultado": resultado, "tabla": tabla, "resumen": resumen}

def analizar_multicolinealidad(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Calcula matriz de correlación y VIF."""
    columnas = columnas_existentes(df, VIF_NUMERIC_COLS)
    X_num = df[columnas].apply(pd.to_numeric, errors="coerce")
    X_num = X_num.fillna(X_num.median())
    X_num = X_num.drop(columns=[col for col in X_num.columns if X_num[col].nunique() <= 1])

    correlacion = X_num.corr()
    X_vif = sm.add_constant(X_num)

    vif = pd.DataFrame(
        {
            "variable": [col for col in X_vif.columns if col != "const"],
            "vif": [
                variance_inflation_factor(X_vif.values, i)
                for i, col in enumerate(X_vif.columns)
                if col != "const"
            ],
        }
    ).sort_values("vif", ascending=False)

    vif["interpretacion"] = pd.cut(
        vif["vif"],
        bins=[-np.inf, 5, 10, np.inf],
        labels=["Sin problema grave", "Multicolinealidad moderada", "Multicolinealidad alta"],
    )

    return correlacion, vif

def interpretar_odds_ratios(tabla_logit: pd.DataFrame) -> pd.DataFrame:
    """Genera una interpretación textual de los odds ratios."""
    tabla = tabla_logit[tabla_logit["variable"] != "const"].copy()
    interpretaciones = []

    for _, fila in tabla.iterrows():
        odds_ratio = fila["odds_ratio"]
        if odds_ratio > 1:
            efecto = "Aumenta las odds de suscripción"
            cambio = (odds_ratio - 1) * 100
        else:
            efecto = "Reduce las odds de suscripción"
            cambio = (1 - odds_ratio) * 100

        interpretaciones.append(
            {
                "variable": fila["variable"],
                "coeficiente": fila["Coef."],
                "pvalor": fila["P>|z|"],
                "odds_ratio": odds_ratio,
                "efecto": efecto,
                "cambio_pct_aprox": cambio,
                "interpretacion": (
                    f"Manteniendo constantes el resto de variables, {fila['variable']} "
                    f"{efecto.lower()} en aproximadamente un {cambio:.2f}%."
                ),
            }
        )

    return pd.DataFrame(interpretaciones).sort_values("pvalor")

def test_normalidad(df: pd.DataFrame, nombre_muestra: str) -> pd.DataFrame:
    """Calcula tests descriptivos de normalidad en variables numéricas."""
    columnas = columnas_existentes(df, [c for c in VIF_NUMERIC_COLS if c != "contacto_previo"])
    resultados = []

    for col in columnas:
        serie = pd.to_numeric(df[col], errors="coerce").dropna()
        if len(serie) < 8:
            continue

        muestra_shapiro = serie.sample(5000, random_state=RANDOM_STATE) if len(serie) > 5000 else serie
        shapiro_stat, shapiro_p = shapiro(muestra_shapiro)
        dagostino_stat, dagostino_p = normaltest(serie)
        jb_stat, jb_p = jarque_bera(serie)

        resultados.append(
            {
                "muestra": nombre_muestra,
                "variable": col,
                "n": len(serie),
                "media": serie.mean(),
                "mediana": serie.median(),
                "desviacion_tipica": serie.std(),
                "asimetria": skew(serie),
                "curtosis": kurtosis(serie),
                "shapiro_pvalor": shapiro_p,
                "dagostino_pvalor": dagostino_p,
                "jarque_bera_pvalor": jb_p,
            }
        )

    return pd.DataFrame(resultados)

def tabla_deciles_desde_probabilidades(y_true: pd.Series, y_proba: np.ndarray, nombre_modelo: str) -> pd.DataFrame:
    """Crea tabla de deciles usando probabilidades fuera de muestra."""
    resultados = pd.DataFrame({"real": y_true.values, "probabilidad": y_proba})
    resultados["decil"] = pd.qcut(
        resultados["probabilidad"].rank(method="first", ascending=False),
        q=10,
        labels=list(range(1, 11)),
    ).astype(int)

    tasa_base = resultados["real"].mean()
    total_suscriptores = resultados["real"].sum()

    deciles = (
        resultados.groupby("decil")
        .agg(
            clientes=("real", "size"),
            suscriptores=("real", "sum"),
            tasa_conversion=("real", "mean"),
            probabilidad_media=("probabilidad", "mean"),
            probabilidad_min=("probabilidad", "min"),
            probabilidad_max=("probabilidad", "max"),
        )
        .reset_index()
        .sort_values("decil")
    )

    deciles["pct_suscriptores"] = deciles["suscriptores"] / total_suscriptores
    deciles["suscriptores_acumulados"] = deciles["suscriptores"].cumsum()
    deciles["gain_acumulado"] = deciles["suscriptores_acumulados"] / total_suscriptores
    deciles["lift"] = deciles["tasa_conversion"] / tasa_base
    deciles["clientes_acumulados"] = deciles["clientes"].cumsum()
    deciles["tasa_conversion_acumulada"] = deciles["suscriptores_acumulados"] / deciles["clientes_acumulados"]
    deciles["lift_acumulado"] = deciles["tasa_conversion_acumulada"] / tasa_base
    deciles["modelo"] = nombre_modelo

    return deciles

def validacion_temporal(df: pd.DataFrame, features: list[str], nombre_modelo: str) -> dict[str, pd.DataFrame] | None:
    """Entrena con datos antiguos y evalúa con datos recientes."""
    if "date_parsed" not in df.columns:
        return None

    datos = df[df["date_parsed"].notna()].sort_values("date_parsed").copy()
    X, y = preparar_xy(datos, features)
    fechas = datos.loc[X.index, "date_parsed"]

    data_temp = X.copy()
    data_temp["subscribed"] = y
    data_temp["date_parsed"] = fechas
    data_temp = data_temp.sort_values("date_parsed")

    corte = int(len(data_temp) * 0.75)
    train = data_temp.iloc[:corte].copy()
    test = data_temp.iloc[corte:].copy()

    X_train = train.drop(columns=["subscribed", "date_parsed"])
    y_train = train["subscribed"].astype(int)
    X_test = test.drop(columns=["subscribed", "date_parsed"])
    y_test = test["subscribed"].astype(int)

    modelo = crear_modelo_logistico(X_train)
    modelo.fit(X_train, y_train)
    evaluacion = evaluar_modelo(nombre_modelo, modelo, X_test, y_test)

    info = pd.DataFrame(
        {
            "elemento": ["modelo", "fecha_min_train", "fecha_max_train", "fecha_min_test", "fecha_max_test", "filas_train", "filas_test"],
            "valor": [
                nombre_modelo,
                train["date_parsed"].min(),
                train["date_parsed"].max(),
                test["date_parsed"].min(),
                test["date_parsed"].max(),
                len(train),
                len(test),
            ],
        }
    )

    return {"info": info, **evaluacion}