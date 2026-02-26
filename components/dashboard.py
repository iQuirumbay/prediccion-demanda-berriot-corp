# components/dashboard.py

import streamlit as st


# def render_dashboard(df):
#     st.success("✅ Archivo validado correctamente")

#     st.markdown("### 📊 Vista previa del inventario")
#     st.dataframe(df, use_container_width=True)

def render_dashboard(df):
    with st.form("form_prediction"):
        
        st.markdown("### 🔎Consulta de ítems")
        st.markdown("---")
        items_selected = []
        items_selected = st.multiselect(
            "Seleccione uno o más ítems",
            sorted(df["ITEM"].unique())
        )
    
        items_validos = len(items_selected) > 0
    
        submit_button = st.form_submit_button(label="Ejecutar")