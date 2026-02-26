# src/prediction/predictor.py
import joblib
import pandas as pd
import numpy as np

MODEL_PATH = "models/modelo_demanda_rf.pkl"
FEATURE_COLUMNS_PATH = "models/feature_columns.pkl"


def predict_demand(df_item: pd.DataFrame) -> float:
    """
    Ejecuta la predicción de demanda para un ítem y devuelve un escalar.
    """

    model = joblib.load(MODEL_PATH)
    feature_columns = joblib.load(FEATURE_COLUMNS_PATH)

    # 🔹 Tomar último registro
    X = df_item[feature_columns].tail(1)

    # 🔹 Asegurar tipo numérico
    X = X.apply(pd.to_numeric, errors="coerce")

    # 🔹 Predicción
    y_pred = model.predict(X)

    # 🔹 NORMALIZACIÓN DEFINITIVA
    if isinstance(y_pred, (list, np.ndarray)):
        return float(y_pred[0])

    return float(y_pred)
