import joblib
import pandas as pd

def load_model_metrics():
    return joblib.load("models/model_metrics.pkl")

def load_item_error():
    return pd.read_csv("models/error_por_item.csv")
