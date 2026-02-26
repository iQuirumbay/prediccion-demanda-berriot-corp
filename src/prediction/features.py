import pandas as pd


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye el conjunto de variables de entrada para el modelo predictivo.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con los datos históricos del ítem seleccionado.

    Returns
    -------
    pd.DataFrame
        DataFrame con las variables listas para el modelo.
    """

    required_columns = [
        "CODITEM",
        "ITEM",
        "LINEA",
        "ANIO",
        "SEMANA",
        "DEMANDA_T_1",
        "DEMANDA_T_2",
        "MEDIA_MOVIL_4",
        "STD_4",
        "ES_CRITICO",
        "STOCK_MINIMO",
    ]

    missing = set(required_columns) - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas requeridas para el modelo: {missing}")

    features = df[required_columns].copy()

    return features
