def compute_suggested_stock(
    predicted_demand,
    error_medio,
    stock_actual,
    stock_minimo
):
    safety_stock = error_medio
    shortage = max(0, stock_minimo - stock_actual)

    return round(predicted_demand + safety_stock + shortage, 2)
