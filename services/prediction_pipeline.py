# services/prediction_pipeline.py

import streamlit as st
import pandas as pd
import joblib
from src.etl.load import load_processed_dataset
from src.prediction.predictor import predict_demand
from src.prediction.metrics import load_item_error
from src.prediction.confidence import compute_confidence
from src.prediction.uncertainty import compute_uncertainty_band
from src.requisition.stock_policy import compute_suggested_stock
from src.requisition.rules import apply_requisition_rules
from src.requisition.generator import generate_requisition_orders


def run_prediction_pipeline(df_user: pd.DataFrame, items_selected: list):

    model, feature_columns = load_model_and_features()
    df_hist = load_hist_dataset()
    error_df = load_error_dataset()

    results = []

    stock_map = dict(zip(df_user["ITEM"], df_user["STOCK_ACTUAL"]))
    items_hist = set(df_hist["ITEM"].unique())
    invalid_items = [i for i in items_selected if i not in items_hist]

    if invalid_items:
        st.warning(f"Los siguientes ítems no existen en histórico: {invalid_items}")
    
    for item in items_selected:

        df_item = df_hist[df_hist["ITEM"] == item].copy()

        if df_item.empty:
            continue

        df_item = df_item.sort_values("SEMANA")

        coditem = df_item["CODITEM"].iloc[-1]
        stock_minimo = float(df_item["STOCK_MINIMO"].iloc[-1])

        # 👇 Ahora el stock viene del CSV usuario
        stock_actual = float(stock_map[item])

        predicted_demand = predict_demand(df_item, model, feature_columns)

        error_item = error_df[error_df["CODITEM"] == coditem]
        error_medio = float(error_item["ERROR_MEDIO"].iloc[0]) if not error_item.empty else 0.0

        confianza, icono = compute_confidence(predicted_demand, error_medio)

        demanda_min, demanda_max = compute_uncertainty_band(
            predicted_demand, error_medio
        )

        stock_sugerido = compute_suggested_stock(
            predicted_demand,
            error_medio,
            stock_actual,
            stock_minimo
        )

        rules = apply_requisition_rules(
            stock_minimo=stock_minimo,
            predicted_demand=predicted_demand,
            stock_actual=stock_actual
        )

        results.append({
            "CODITEM": coditem,
            "ITEM": item,
            "DEMANDA_PREDICHA": round(predicted_demand, 2),
            "DEMANDA_MIN": round(demanda_min, 2),
            "DEMANDA_MAX": round(demanda_max, 2),
            "ERROR_HISTORICO": round(error_medio, 2),
            "CONFIANZA": f"{icono} {confianza}",
            "STOCK_ACTUAL": stock_actual,
            "STOCK_MINIMO": stock_minimo,
            "STOCK_SUGERIDO": stock_sugerido,
            **rules
        })

    results_df = pd.DataFrame(results)
    requisitions_df = generate_requisition_orders(results_df)

    return results_df, requisitions_df

@st.cache_resource
def load_model_and_features():
    model = joblib.load("models/modelo_demanda_rf.pkl")
    feature_columns = joblib.load("models/feature_columns.pkl")
    return model, feature_columns


@st.cache_data
def load_hist_dataset():
    return load_processed_dataset("data/processed/df_model.csv")


@st.cache_data
def load_error_dataset():
    return load_item_error()