def compare_floats(x, y, tolerance=0.00001):
    return abs(x - y) < tolerance

def find_closest_value(value, values):
    '''
    Find the index of the closest value to the given value in the list of values.
    '''

    return min(range(len(values)), key=lambda i: abs(values[i] - value))
