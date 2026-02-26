# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from src.etl.load import load_items_catalog, load_processed_dataset
from src.prediction.predictor import predict_demand
from src.prediction.metrics import load_item_error
from src.prediction.confidence import compute_confidence
from src.prediction.uncertainty import compute_uncertainty_band
from src.requisition.stock_policy import compute_suggested_stock
from src.requisition.rules import apply_requisition_rules
from src.requisition.generator import generate_requisition_orders


# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================
st.set_page_config(
    page_title="Predicción de Demanda - Berriot Corp",
    layout="wide"
)

st.title("📦 Predicción de Demanda de Insumos Críticos")
st.markdown(
    "Sistema de apoyo a la toma de decisiones para la gestión de inventarios."
)

st.info(
    "La predicción corresponde al próximo período operativo y debe "
    "utilizarse como apoyo a la decisión, no como reposición automática."
)


# =====================================================
# CARGA DE DATOS
# =====================================================
items_df = load_items_catalog()
df_hist = load_processed_dataset("data/processed/df_model.csv")
error_df = load_item_error()


# =====================================================
# FORMULARIO DE ENTRADA
# =====================================================
with st.form("form_prediccion"):

    modo_consulta = st.radio(
        "Seleccione el método de consulta",
        ["Seleccionar ítem", "Seleccionar múltiples ítems", "Cargar archivo CSV"]
    )

    items_selected = []

    if modo_consulta == "Seleccionar ítem":
        item = st.selectbox(
            "Seleccione un ítem crítico",
            items_df["ITEM"].unique()
        )
        items_selected = [item]

    elif modo_consulta == "Seleccionar múltiples ítems":
        items_selected = st.multiselect(
            "Seleccione uno o más ítems críticos",
            items_df["ITEM"].unique()
        )

    elif modo_consulta == "Cargar archivo CSV":
        uploaded_file = st.file_uploader("Cargue el archivo CSV", type=["csv"])
        if uploaded_file:
            items_selected = pd.read_csv(uploaded_file)["ITEM"].tolist()

    st.markdown("### Stock actual por ítem")

    stock_inputs = {}
    for item in items_selected:
        stock_inputs[item] = st.number_input(
            f"Stock actual de {item}",
            min_value=0,
            value=0,
            key=f"stock_{item}"
        )

    submit = st.form_submit_button("Ejecutar predicción")


# =====================================================
# EJECUCIÓN
# =====================================================
if submit and items_selected:

    results = []

    for item in items_selected:

        df_item = df_hist[df_hist["ITEM"] == item].copy()
        if df_item.empty:
            continue

        df_item = df_item.sort_values("SEMANA")

        # -----------------------------
        # Datos base
        # -----------------------------
        coditem = df_item["CODITEM"].iloc[-1]
        stock_minimo = float(df_item["STOCK_MINIMO"].iloc[-1])
        stock_actual = float(stock_inputs[item])

        # -----------------------------
        # Predicción
        # -----------------------------
        predicted_demand = float(predict_demand(df_item))

        # -----------------------------
        # Error histórico por ítem
        # -----------------------------
        error_item = error_df[error_df["CODITEM"] == coditem]
        error_medio = (
            float(error_item["ERROR_MEDIO"].iloc[0])
            if not error_item.empty
            else predicted_demand
        )

        # -----------------------------
        # Confianza
        # -----------------------------
        confianza, icono = compute_confidence(
            predicted_demand,
            error_medio
        )

        # -----------------------------
        # Incertidumbre
        # -----------------------------
        demanda_min, demanda_max = compute_uncertainty_band(
            predicted_demand,
            error_medio
        )

        # -----------------------------
        # Stock sugerido
        # -----------------------------
        stock_sugerido = compute_suggested_stock(
            predicted_demand=predicted_demand,
            error_medio=error_medio,
            stock_actual=stock_actual,
            stock_minimo=stock_minimo
        )

        # -----------------------------
        # Reglas
        # -----------------------------
        rules = apply_requisition_rules(
            stock_actual=stock_actual,
            stock_minimo=stock_minimo,
            predicted_demand=predicted_demand
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

    # =================================================
    # RESULTADOS TABULARES
    # =================================================
    st.subheader("📋 Resultados de la predicción")
    st.dataframe(results_df, use_container_width=True)

    # =================================================
    # GRÁFICAS
    # =================================================
    st.subheader("📊 Análisis visual por ítem")

    for _, row in results_df.iterrows():

        item = row["ITEM"]
        df_item = df_hist[df_hist["ITEM"] == item].sort_values("SEMANA")

        # ---------- DEMANDA ----------
        fig, ax = plt.subplots(figsize=(8, 4))

        ax.plot(
            df_item["SEMANA"],
            df_item["DEMANDA"],
            marker="o",
            label="Demanda histórica"
        )

        ax.axhline(
            row["DEMANDA_PREDICHA"],
            linestyle="--",
            label="Demanda predicha"
        )

        ax.fill_between(
            [df_item["SEMANA"].iloc[-1], df_item["SEMANA"].iloc[-1]],
            row["DEMANDA_MIN"],
            row["DEMANDA_MAX"],
            alpha=0.25,
            label="Rango esperado"
        )

        ax.set_title(f"Demanda – {item}")
        ax.set_xlabel("Periodo")
        ax.set_ylabel("Unidades")
        ax.legend()

        st.pyplot(fig)

        # ---------- STOCK ----------
        fig, ax = plt.subplots(figsize=(5, 4))

        ax.bar(
            ["Stock actual", "Stock mínimo", "Stock sugerido"],
            [
                row["STOCK_ACTUAL"],
                row["STOCK_MINIMO"],
                row["STOCK_SUGERIDO"]
            ]
        )

        ax.set_title(f"Stock – {item}")
        ax.set_ylabel("Unidades")

        st.pyplot(fig)

    # =================================================
    # REPOSICIONES
    # =================================================
    if not requisitions_df.empty:
        st.warning("⚠️ Ítems que requieren reposición")
        st.dataframe(requisitions_df, use_container_width=True)

        st.download_button(
            "Descargar órdenes sugeridas",
            requisitions_df.to_csv(index=False),
            file_name="ordenes_requisicion_sugeridas.csv"
        )
    else:
        st.success("No se requieren reposiciones para el período evaluado")

    # =================================================
    # LEYENDA
    # =================================================
    st.markdown("### 🧭 Interpretación del nivel de confianza")
    st.markdown(
        """
- 🟢 **Alta**: Predicción estable, puede utilizarse directamente.  
- 🟡 **Media**: Predicción razonable, se recomienda revisión.  
- 🔴 **Baja**: Alta incertidumbre, decisión manual recomendada.
"""
    )
