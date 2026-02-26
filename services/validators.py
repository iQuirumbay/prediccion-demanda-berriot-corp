# services/validators.py

REQUIRED_COLUMNS = {"ITEM","STOCK_ACTUAL"}


def validate_file_type(uploaded_file):
    """
    Validacion del tipo de archivo (csv o xlsx)
    """
    return uploaded_file.name.endswith((".csv", ".xlsx"))

def validate_structure(df):
    """
    Valida estructura normalizando nombres de columnas
    """

    normalized_columns = (
        df.columns
        .str.strip()
        .str.upper()
    )

    return REQUIRED_COLUMNS.issubset(set(normalized_columns))
