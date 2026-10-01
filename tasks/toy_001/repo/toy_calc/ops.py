def calculate_discount(price: float, percent: float) -> float:
    """Return the price after applying a percentage discount."""
    # BUG: percent should be divided by 100 before use
    return price - (price * percent)
