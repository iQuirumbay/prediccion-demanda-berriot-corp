# services/prediction_pipeline.py

import pandas as pd

from src.etl.load import load_processed_dataset
from src.prediction.predictor import predict_demand
from src.prediction.metrics import load_item_error
from src.prediction.confidence import compute_confidence
from src.prediction.uncertainty import compute_uncertainty_band
from src.requisition.stock_policy import compute_suggested_stock
from src.requisition.rules import apply_requisition_rules
from src.requisition.generator import generate_requisition_orders


def run_prediction_pipeline(df_user: pd.DataFrame, items_selected: list):

    df_hist = load_processed_dataset("data/processed/df_model.csv")
    error_df = load_item_error()

    results = []

    for item in items_selected:

        df_item = df_hist[df_hist["ITEM"] == item].copy()

        if df_item.empty:
            continue

        df_item = df_item.sort_values("SEMANA")

        coditem = df_item["CODITEM"].iloc[-1]
        stock_minimo = float(df_item["STOCK_MINIMO"].iloc[-1])

        # 👇 Ahora el stock viene del CSV usuario
        stock_actual = float(
            df_user[df_user["ITEM"] == item]["STOCK_ACTUAL"].iloc[0]
        )

        predicted_demand = float(predict_demand(df_item))

        error_item = error_df[error_df["CODITEM"] == coditem]
        error_medio = (
            float(error_item["ERROR_MEDIO"].iloc[0])
            if not error_item.empty
            else 0
        )

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