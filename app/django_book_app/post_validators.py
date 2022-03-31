import string
import re


def post_isbn_verificate(isbn):
    wrong_ch = 0
    nums = 0
    dashes = 0
    for ch in isbn:
        if not ch.isnumeric() and not ch == '-':
            wrong_ch += 1
    if wrong_ch != 0:
        return False
    else:
        nums = [int(i) for i in isbn if i.isdigit()]
        nums = len(nums)
        for ch in isbn:
            if ch == '-':
                dashes += 1
        if nums == 9 and dashes == 3:
            return True
        if nums == 13 and dashes == 4:
            return True
        return False
