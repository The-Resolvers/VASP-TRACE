def calculate_proximity_score(hops: int) -> float:
    """
    S_{prox} = 1 / (2^(hops - 1))
    """
    if hops <= 0:
        return 1.0
    return 1.0 / (2 ** (hops - 1))

def calculate_composite_score(proximity: float, ml_prob: float, has_tag: bool) -> float:
    """
    Composite Confidence Score combining Proximity math, ML probability, and Tag matches.
    """
    if has_tag:
        return 1.0 # Ground truth
        
    # Example weighting: 40% proximity, 60% ML
    return (0.4 * proximity) + (0.6 * ml_prob)
