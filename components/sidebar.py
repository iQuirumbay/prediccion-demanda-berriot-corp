# components/sidebar.py

import streamlit as st


def render_sidebar():
    st.sidebar.header("📂 Carga de Reporte")

    uploaded_file = st.sidebar.file_uploader(
        "Suba un archivo CSV o XLSX",
        type=["csv", "xlsx"]
    )

    return uploaded_file

def render_sidebar_preview(df):
    st.sidebar.success("✅ Archivo cargado correctamente")
    st.sidebar.markdown("### 📊 Vista previa")
    st.sidebar.dataframe(df, use_container_width=True)