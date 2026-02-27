# components/dashboard.py
import io
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from src.etl.load import load_processed_dataset
from services.pdf_generator import generate_pdf

def render_dashboard(df):
    with st.container():
        with st.form("form_prediction"):            
            st.markdown("### 🔎 Consulta de ítems")
            items_selected = st.multiselect(
                "Seleccione uno o más ítems",
                sorted(df["ITEM"].unique())
            )

            submit_button = st.form_submit_button(label="Ejecutar")

    return submit_button, items_selected

def render_results(results_df, requisitions_df):

    df_hist = load_processed_dataset("data/processed/df_model.csv")

    if results_df.empty:
        st.warning("No hay resultados para mostrar.")
        return

    plt.close('all')
    st.markdown("## 📊 Resultados por ítem")

    for _, row in results_df.iterrows():

        item = row["ITEM"]
        df_item = df_hist[df_hist["ITEM"] == item].sort_values("SEMANA")

        with st.expander(f"{item} (CODITEM {row['CODITEM']})", expanded=True):

            col_metrics, col_error, col_stock, col_graf_demanda, col_graf_stock = st.columns([10,10,10,10,10])

            # 🔹 Métricas
            with col_metrics:
                st.metric("Demanda Predicha", row["DEMANDA_PREDICHA"])
                st.metric("Demanda Mínima", row["DEMANDA_MIN"])
                st.metric("Demanda Máxima", row["DEMANDA_MAX"])

            with col_error:
                st.metric("Error Histórico", row["ERROR_HISTORICO"])
                st.metric("Confianza", row["CONFIANZA"])

            with col_stock:
                st.metric("Stock Actual", row["STOCK_ACTUAL"])
                st.metric("Stock Mínimo", row["STOCK_MINIMO"])
                st.metric("Stock Sugerido", row["STOCK_SUGERIDO"])

            # 🔹 Gráfica Demanda
            with col_graf_demanda:

                fig1, ax1 = plt.subplots(figsize=(8, 4))

                ax1.plot(
                    df_item["SEMANA"],
                    df_item["DEMANDA"],
                    marker="o",
                    label="Histórica"
                )

                ax1.axhline(
                    row["DEMANDA_PREDICHA"],
                    linestyle="--",
                    label="Predicción"
                )

                ax1.fill_between(
                    df_item["SEMANA"],
                    row["DEMANDA_MIN"],
                    row["DEMANDA_MAX"],
                    alpha=0.2,
                    label="Rango esperado"
                )

                ax1.set_title(f"Evolución de Demanda de {item}")
                ax1.legend()

                st.pyplot(fig1)

            # 🔹 Gráfica Stock
            with col_graf_stock:

                fig2, ax2 = plt.subplots(figsize=(8, 4))

                ax2.bar(
                    ["Actual", "Mínimo", "Sugerido"],
                    [
                        row["STOCK_ACTUAL"],
                        row["STOCK_MINIMO"],
                        row["STOCK_SUGERIDO"]
                    ]
                )

                ax2.set_title(f"Nivel de Stock de {item}")

                st.pyplot(fig2)

    # 🔹 Órdenes
    st.markdown("## 🛒 Órdenes de Requisición")

    if not requisitions_df.empty:
        st.warning("⚠ Ítems que requieren reposición")
        st.dataframe(requisitions_df)
        if not requisitions_df.empty:
            st.markdown("### 📥 Descargar Órdenes")
            col1, col2 = st.columns(2)
        # ---- EXCEL ----
        with col1:
            buffer = io.BytesIO()

            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                requisitions_df.to_excel(writer, index=False, sheet_name="Ordenes")

            st.download_button(
                label="⬇ Descargar en Excel",
                data=buffer.getvalue(),
                file_name="ordenes_requisicion.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        with col2:
            pdf_buffer = generate_pdf(requisitions_df)
            st.download_button(
                label="⬇ Descargar en PDF",
                data=pdf_buffer,
                file_name="ordenes_requisicion.pdf",
                mime="application/pdf"
            )
    else:
        st.success("No se requieren reposiciones.")

