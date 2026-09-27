def transpose_rectangular(matrix):
    if not matrix:
        return []

    row_length = len(matrix[0])
    for row in matrix:
        if len(row) != row_length:
            raise ValueError("row lengths differ")

    if row_length == 0:
        return []

    return [[row[col] for row in matrix] for col in range(row_length)]
