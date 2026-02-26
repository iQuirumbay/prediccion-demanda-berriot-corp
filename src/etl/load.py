from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]


DATASET_PROCESSED_PATH = "data/processed/df_model_features.csv"
DATASET_ITEMCATALOG_PATH = "data/processed/df_model.csv"

def load_processed_dataset(
    relative_path: str = DATASET_PROCESSED_PATH
) -> pd.DataFrame:
    """
    Carga el dataset consolidado utilizado para el modelo predictivo.
    """
    path = BASE_DIR / relative_path

    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {path}")

    return pd.read_csv(path)


def load_items_catalog(
    relative_path: str = DATASET_ITEMCATALOG_PATH
) -> pd.DataFrame:
    """
    Carga el catálogo de ítems disponibles para predicción.
    """
    path = BASE_DIR / relative_path

    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {path}")

    df = pd.read_csv(path)

    return df[
        ["CODITEM", "ITEM", "LINEA", "ES_CRITICO", "STOCK_MINIMO"]
    ].drop_duplicates()

# ----------------------------------------------------
# Carga de CSV proporcionado por el usuario (Streamlit)
# ----------------------------------------------------
def load_user_input_csv(uploaded_file) -> pd.DataFrame:
    """
    Carga un archivo CSV subido por el usuario desde Streamlit.

    Parameters
    ----------
    uploaded_file : UploadedFile
        Archivo cargado mediante st.file_uploader().

    Returns
    -------
    pd.DataFrame
        DataFrame con los ítems a consultar y stock actual.
    """
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        raise ValueError(f"Error al leer el archivo CSV: {e}")

    required_columns = {"CODITEM", "STOCK_ACTUAL"}

    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(
            f"El archivo debe contener las columnas: {required_columns}"
        )

    return df
