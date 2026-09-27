def is_palindrome_normalized(text):
    left = 0
    right = len(text) - 1

    while left < right:
        while left < right and not (
            ("A" <= text[left] <= "Z")
            or ("a" <= text[left] <= "z")
            or ("0" <= text[left] <= "9")
        ):
            left += 1

        while left < right and not (
            ("A" <= text[right] <= "Z")
            or ("a" <= text[right] <= "z")
            or ("0" <= text[right] <= "9")
        ):
            right -= 1

        a = text[left]
        b = text[right]

        if "A" <= a <= "Z":
            a = chr(ord(a) + 32)
        if "A" <= b <= "Z":
            b = chr(ord(b) + 32)

        if a != b:
            return False

        left += 1
        right -= 1

    return True
