from toy_calc.ops import calculate_discount


def test_twenty_percent_off():
    assert calculate_discount(100, 20) == 80


def test_zero_percent_off():
    assert calculate_discount(50, 0) == 50


def test_fifty_percent_off():
    assert calculate_discount(200, 50) == 100
