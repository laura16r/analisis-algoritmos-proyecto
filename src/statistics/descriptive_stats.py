from typing import Optional

def calculate_mean(values: list[float]) -> Optional[float]:
    """
    Calcula la media aritmética manualmente.

    Fórmula:
        media = suma_valores / cantidad_valores
    """

    if not values:
            return None
    
    total = 0.0

    for value in values:
            total += value

    return total / len(values)

def calculate_variance(
    values: list[float],
    sample: bool = True,
) -> Optional[float]:
    """
    Calcula la varianza manualmente.

    Args:
        values: Lista de valores numéricos.
        sample:
            True  -> varianza muestral, divide entre n-1.
            False -> varianza poblacional, divide entre n.

    Returns:
        Varianza calculada o None si no se puede calcular
    """

    if not values:
        return None
    
    if sample and len(values) < 2:
        return None
    
    mean = calculate_mean(values)

    if mean is None:
        return None
    
    squared_differences_sum = 0.0

    for value in values:
         difference = value - mean
         squared_differences_sum += difference ** 2

    divisor = len(values) - 1 if sample else len(values)

    return squared_differences_sum / divisor


def calculate_standard_deviation(
    values: list[float],
    sample: bool = True,
) -> Optional[float]:
    """
    Calcula la desviación estándar manualmente.

    Fórmula:
        desviación_estándar = raiz_cuadtrada(varianza)
    """

    variance = calculate_variance(values, sample=sample)

    if variance is None:
        return None
    
    return variance ** 0.5