def summarize_ranges(nums):
    ranges = []
    if not nums:
        return ranges

    start = prev = nums[0]
    for num in nums[1:]:
        if num != prev + 1:
            ranges.append(str(start) if start == prev else f"{start}-{prev}")
            start = num
        prev = num

    ranges.append(str(start) if start == prev else f"{start}-{prev}")
    return ranges
