from toy_calc.ops import calculate_sum_to_n

def test_sum_40_to_45():
    assert calculate_sum_to_n(40,45)==255

def test_sum_30_to_40():
    assert calculate_sum_to_n(30,40)==385

def test_sum_13_to_29():
    assert calculate_sum_to_n(13, 29)==357 