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
st.markdown("Sistema de apoyo a la toma de decisiones para la gestión de inventarios.")

col_left, col_right = st.columns([40, 60])


# =====================================================
# CARGA DE DATOS
# =====================================================
items_df = load_items_catalog()
df_hist = load_processed_dataset("data/processed/df_model.csv")
error_df = load_item_error()

# =====================================================
# SECCIÓN IZQUIERDA – FORMULARIO
# =====================================================
with col_left:
        # Modo de consulta para seleccionar ítems
        modo_consulta = st.radio(
            "Seleccione el método de consulta",
            ["Seleccionar ítem", "Seleccionar múltiples ítems", "Cargar archivo CSV"]
        )
        
        items_selected = [] # Lista para almacenar los ítems seleccionados
        
        if modo_consulta == "Seleccionar ítem":
            item = st.selectbox(
                "Seleccione un ítem",
                items_df["ITEM"].unique(),
                index=None,
                placeholder="Elige una opción"
            )
            if item is not None:
                items_selected = [item] 
        
        elif modo_consulta == "Seleccionar múltiples ítems":
            items_selected = st.multiselect(
                "Seleccione uno o más ítems",
                items_df["ITEM"].unique()
            )
        elif modo_consulta == "Cargar archivo CSV":
            uploaded_file = st.file_uploader("Cargue un archivo CSV con una columna 'ITEM'", type="csv")
            if uploaded_file is not None:
                try:
                    df_uploaded = pd.read_csv(uploaded_file)
                    if 'ITEM' in df_uploaded.columns:
                        items_selected = df_uploaded['ITEM'].dropna().unique().tolist()
                    else:
                        st.error("El archivo CSV debe contener una columna llamada 'ITEM'.")
                except Exception as e:
                    st.error(f"Error al leer el archivo CSV: {e}")
        
        items_validos = len(items_selected) > 0
        
        with st.form("form_prediccion"):
            st.markdown("### Stock actual por ítem:")
            stock_inputs = {}
            for item in items_selected:
                stock_inputs[item] = st.number_input(f"Stock actual de {item}", min_value=0, value=0, key=f"stock_{item}")
            # Botón para ejecutar la predicción
            submit_button = st.form_submit_button(label="Ejecutar Predicción", disabled=not items_validos)
            

# =====================================================
#Ejecución de la predicción
# =====================================================
results = []

if submit_button and items_selected:
    for item in items_selected:
        df_item = df_hist[df_hist["ITEM"] == item].copy()
        if df_item.empty:
            st.warning(f"No hay datos históricos para el ítem '{item}'. No se puede realizar la predicción.")
            continue
        
        df_item = df_item.sort_values("SEMANA").reset_index(drop=True)
        
        coditem = df_item["CODITEM"].iloc[-1]
        stock_minimo = float(df_item["STOCK_MINIMO"].iloc[-1])
        stock_actual = float(stock_inputs[item])
        
        predicted_demand = float(predict_demand(df_item))
        
        error_item = error_df[error_df["CODITEM"] == coditem]
        error_medio = (float(error_item["ERROR_MEDIO"].iloc[0]) if not error_item.empty else predict_demand)
        
        confianza, icono = compute_confidence(predicted_demand,error_medio)
        demanda_min, demanda_max = compute_uncertainty_band(predicted_demand, error_medio)
        
        stock_sugerido = compute_suggested_stock(predicted_demand, error_medio, stock_actual, stock_minimo)
        
        rules = apply_requisition_rules(stock_actual, stock_minimo, predicted_demand)
        
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

# =====================================================
# SECCIÓN IZQUIERDA - RESULTADOS
# =====================================================
with col_left:
    results_df = pd.DataFrame(results)
    requisitions_df = generate_requisition_orders(results_df)
    if not results_df.empty:
        st.subheader("📋 Resultados de la predicción")
        #Mostrar los resultados con tarjetas por item
        for _, row in results_df.iterrows():
            st.markdown(f"### 🧱{row['ITEM']} (CODITEM: {row['CODITEM']})")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Demanda Predicha", f"{row['DEMANDA_PREDICHA']}")
                st.metric("Demanda Mínima", f"{row['DEMANDA_MIN']}")
                st.metric("Demanda Máxima", f"{row['DEMANDA_MAX']}")
            with col2:
                st.metric("Error Histórico", f"{row['ERROR_HISTORICO']}")
                st.metric("Confianza", row["CONFIANZA"])
            with col3:
                st.metric("Stock Actual", f"{row['STOCK_ACTUAL']}")
                st.metric("Stock Mínimo", f"{row['STOCK_MINIMO']}")
                st.metric("Stock Sugerido", f"{row['STOCK_SUGERIDO']}") 
    
    if not requisitions_df.empty:
        st.warning("⚠️ Ítems que requieren reposición")
        st.download_button(
            "Descargar órdenes sugeridas",
            requisitions_df.to_csv(index=False),
            file_name="ordenes_requisicion_sugeridas.csv"
        )
    else:
        st.success("No se requieren reposiciones para el período evaluado") 

# =====================================================
# SECCIÓN DERECHA - ANÁLISIS (GRÁFICOS)
# =====================================================
with col_right:

    if not results_df.empty:
        st.subheader("📊 Evolución temporal")

        for _, row in results_df.iterrows():
            item = row["ITEM"]
            df_item = df_hist[df_hist["ITEM"] == item].sort_values("SEMANA")

            # ----- DEMANDA -----
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(df_item["SEMANA"], df_item["DEMANDA"], marker="o", label="Histórica")
            ax.axhline(row["DEMANDA_PREDICHA"], linestyle="--", label="Predicción")
            ax.fill_between(
                [df_item["SEMANA"].iloc[-1], df_item["SEMANA"].iloc[-1]],
                row["DEMANDA_MIN"],
                row["DEMANDA_MAX"],
                alpha=0.3,
                label="Rango esperado"
            )
            ax.set_title(f"Demanda – {item}")
            ax.legend()
            st.pyplot(fig)

            # ----- STOCK -----
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.bar(
                ["Actual", "Mínimo", "Sugerido"],
                [row["STOCK_ACTUAL"], row["STOCK_MINIMO"], row["STOCK_SUGERIDO"]]
            )
            ax.set_title(f"Stock – {item}")
            st.pyplot(fig)