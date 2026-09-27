def first_unique_index(text):
    from collections import Counter

    counts = Counter(text)
    for index, character in enumerate(text):
        if counts[character] == 1:
            return index
    return -1
