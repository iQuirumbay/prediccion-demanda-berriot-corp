import pandas as pd

def load_file(uploaded_file):
    """
    Carga archivo CSV o XLSX detectando separador automáticamente
    """

    try:
        if uploaded_file.name.endswith(".csv"):

            # Intentar primero con coma
            df = pd.read_csv(uploaded_file)

            # Si solo detecta una columna, probablemente es ;
            if len(df.columns) == 1:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, sep=";")

        else:
            df = pd.read_excel(uploaded_file)

        return df

    except Exception:
        return None


def clean_data(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
    )

    df["ITEM"] = df["ITEM"].astype(str).str.strip()
    df["STOCK_ACTUAL"] = pd.to_numeric(df["STOCK_ACTUAL"], errors="coerce")

    return df
