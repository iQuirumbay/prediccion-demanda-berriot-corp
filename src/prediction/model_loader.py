import joblib
import os

from typing import Tuple

#Función para cargar el modelo y el scaler
#Ruta del modelo model_path = str "models/modelo_demanda_rf.pkl"
#Ruta del scaler scaler_path = str "models/scaler_demanda_rf.pkl"
def load_model_and_scaler(
    model_path:  str = "models/modelo_demanda_rf.pkl",
    scaler_path: str | None = None
) -> Tuple[object, object | None]:

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"No se encontró el modelo en la ruta especificada: {model_path}"
        )

    model = joblib.load(model_path)

    scaler = None
    if scaler_path:
        if not os.path.exists(scaler_path):
            raise FileNotFoundError(
                f"No se encontró el scaler en la ruta especificada: {scaler_path}"
            )
        scaler = joblib.load(scaler_path)

    return model, scaler