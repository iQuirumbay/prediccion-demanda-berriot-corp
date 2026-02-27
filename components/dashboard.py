# components/dashboard.py

import streamlit as st

def render_dashboard(df):
    with st.container():
        with st.form("form_prediction"):
            
            st.markdown("### 🔎 Consulta de ítems")
            st.markdown("---")

            items_selected = st.multiselect(
                "Seleccione uno o más ítems",
                sorted(df["ITEM"].unique())
            )

            submit_button = st.form_submit_button(label="Ejecutar")

    return submit_button, items_selected