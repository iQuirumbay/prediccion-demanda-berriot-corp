def compute_confidence(predicted_demand, error_medio):
    if predicted_demand <= 0:
        return "BAJA", "🔴"

    ratio = error_medio / predicted_demand

    if ratio <= 0.20:
        return "ALTA", "🟢"
    elif ratio <= 0.40:
        return "MEDIA", "🟡"
    else:
        return "BAJA", "🔴"
