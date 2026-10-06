def find_max(numbers: list[int])->int:
    """ Return the maximum from the list. """
    # BUG : there should not be a else statement.
    maxi= numbers[0]
    for i in numbers:
        if numbers[i]>maxi:
            maxi= numbers[i]
        else:
            break
    return maxi
