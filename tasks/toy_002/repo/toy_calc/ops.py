def calculate_sum_to_n(start: int, end:int) -> int:
    """ Return the sum from start to end. """
    # BUG: the 'end' is not getting added
    sum=0
    for i in range (start, end):
        sum+= i
    return sum
    