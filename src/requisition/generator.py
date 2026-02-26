import pandas as pd

def generate_requisition_orders(results_df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera un DataFrame con las órdenes de requisición sugeridas
    a partir de los resultados del modelo y las reglas de negocio.
    """

    requisitions = []

    for _, row in results_df.iterrows():

        if row["needs_requisition"]:

            requisitions.append({
                "CODITEM": row["CODITEM"],
                "ITEM": row["ITEM"],
                "STOCK ACTUAL": row["STOCK_ACTUAL"],
                "STOCK MINIMO": row["STOCK_MINIMO"],
                "CANTIDAD A REPONER": row["quantity_to_order"],
            })

    return pd.DataFrame(requisitions)
