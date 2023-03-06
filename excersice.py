def find_max(nums):
    max_num = float("-inf")  # smaller than all other numbers
    print(max_num)
    for num in nums:
        if num > max_num:
            max_num = num
    # (Fill in the missing line here)
    return max_num


print(find_max([2, 8, 9, 10]))
