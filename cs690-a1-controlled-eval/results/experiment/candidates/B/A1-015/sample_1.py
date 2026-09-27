def window_sums(values, width):
    if width <= 0:
        raise ValueError("width must be positive")
    if width > len(values):
        return []

    current = sum(values[:width])
    result = [current]

    for index in range(width, len(values)):
        current += values[index] - values[index - width]
        result.append(current)

    return result
