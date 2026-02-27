# app.py

import streamlit as st
from PIL import Image
from services.file_loader import load_file, clean_data
from services.validators import validate_file_type, validate_structure
from services.prediction_pipeline import run_prediction_pipeline
from components.sidebar import render_sidebar, render_sidebar_preview
from components.dashboard import render_dashboard, render_results
# ======================================================
# CONFIGURACIÓN GENERAL
# ======================================================

st.set_page_config(
    page_title="Sistema Predictivo de Inventario",
    layout="wide"
)

logo = Image.open("assets/berriot_logo.png")
col_title, col_logo = st.columns( [60, 40])
with col_title:
    st.title("📦 Predicción de Demanda de Insumos Críticos")

with col_logo:
    st.image(logo, width=450)
st.markdown("Sistema de apoyo a la toma de decisiones para la gestión de inventarios.")

# ======================================================
# SIDEBAR
# ======================================================

uploaded_file = render_sidebar()

# ======================================================
# FLUJO PRINCIPAL
# ======================================================

if uploaded_file:

    # Validación tipo archivo
    if not validate_file_type(uploaded_file):
        st.error("❌ El archivo debe ser formato CSV o XLSX.")
        st.stop()

    # Cargar archivo
    df = load_file(uploaded_file)
    #st.write("Columnas detectadas:")
    #st.write(df.columns.tolist())


    if df is None:
        st.error("❌ Error al leer el archivo.")
        st.stop()

    # Validar estructura
    if not validate_structure(df):
        st.error(
            """
            ❌ El archivo no contiene la estructura correcta.

            Debe incluir las columnas obligatorias:
            - ITEM
            - STOCK_ACTUAL
            """
        )
        st.stop()

    # Limpieza
    df = clean_data(df)

    # Validación adicional opcional
    if df["STOCK_ACTUAL"].isnull().any():
        st.warning("⚠ Algunos valores de STOCK_ACTUAL no son numéricos.")

    # Renderizar el SideBoard Preview
    render_sidebar_preview(df)

    submit_button, items_selected = render_dashboard(df)

    if submit_button and items_selected:

        from services.prediction_pipeline import run_prediction_pipeline

        results_df, requisitions_df = run_prediction_pipeline(
            df_user=df,
            items_selected=items_selected
        )

    render_results(results_df, requisitions_df)

    #st.markdown("## 📊 Resultados")

   # st.dataframe(results_df, use_container_width=True)

    #st.markdown("## 🛒 Órdenes sugeridas")

    #if not requisitions_df.empty:
     #   st.warning("⚠ Ítems que requieren reposición")
      #  st.dataframe(requisitions_df)
    #else:
     #   st.success("No se requieren reposiciones.")

else:
    st.info("📂 Cargue un archivo para comenzar.")