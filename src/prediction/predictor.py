# src/prediction/predictor.py

import pandas as pd
import numpy as np


def predict_demand(df_item: pd.DataFrame, model, feature_columns) -> float:
    """
    Ejecuta la predicción de demanda para un ítem y devuelve un escalar.
    """

    X = df_item[feature_columns].tail(1)
    X = X.apply(pd.to_numeric, errors="coerce")

    y_pred = model.predict(X)

    if isinstance(y_pred, (list, np.ndarray)):
        return float(y_pred[0])

    return float(y_pred)