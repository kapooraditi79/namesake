from toy_calc.ops import find_max


def test_finds_maximum():
    assert find_max([5, 8, 3, 10]) == 10


def test_maximum_at_start():
    assert find_max([10, 5, 3, 2]) == 10


def test_maximum_at_end():
    assert find_max([2, 4, 6, 10]) == 10


def test_single_element():
    assert find_max([7]) == 7


def test_empty_list():
    assert find_max([]) is None