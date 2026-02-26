def compute_uncertainty_band(predicted_demand, error_medio):
    lower = max(0, predicted_demand - error_medio)
    upper = predicted_demand + error_medio
    return lower, upper
