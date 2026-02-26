def apply_requisition_rules(stock_minimo, predicted_demand, stock_actual):
    """
    Aplica reglas de reposición basadas en la demanda predicha.
    """

    stock_minimo = float(stock_minimo)
    predicted_demand = float(predicted_demand)
    stock_actual = float(stock_actual)

    reorder_point = stock_minimo + predicted_demand
    needs_requisition = stock_actual < reorder_point
    quantity_to_order = max(0, reorder_point - stock_actual)

    return {
        "reorder_point": reorder_point,
        "needs_requisition": needs_requisition,
        "quantity_to_order": quantity_to_order,
    }
