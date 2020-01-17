import string


def is_isin_valid(string_isin):
    """
    Checks a given ISIN for validity
    reference to: https://en.wikipedia.org/wiki/International_Securities_Identification_Number
    reference to: http://code.activestate.com/recipes/498277-isin-validator/
    :param string_isin:
    :return:
    """

    # check the ISIN to be exactly 12 alphanumeric characters
    if len(string_isin) != 12 or not string_isin.isalnum():
        return None
    
    # check the ISIN to start with two letters
    if not string_isin[:2].isalpha():
        return None

    # check the ISIN to end with a digit
    if not string_isin[-1].isnumeric():
        return None

    list_isin_parts = []

    # Convert alpha characters to digits
    for each_char in string_isin:
        if each_char.isdigit():
            list_isin_parts.append(int(each_char))
        else:
            # increase alphabetical index by 9
            list_isin_parts.append(string.ascii_uppercase.index(each_char.upper()) + 9 + 1)

    # last digit serves as check digit
    check_digit = list_isin_parts[-1]

    list_isin_parts = list_isin_parts[:-1]

    # convert each int into a string
    list_isin_parts = ''.join([str(i) for i in list_isin_parts])

    # separate even and odd indices
    isin_even = list_isin_parts[::2]
    isin_odd = list_isin_parts[1::2]

    # If len(isin2) is odd, multiply evens by 2, else multiply odds by 2
    if len(list_isin_parts) % 2 > 0:
        isin_even = ''.join([str(int(i)*2) for i in list(isin_even)])
    else:
        isin_odd = ''.join([str(int(i)*2) for i in list(isin_odd)])

    even_sum = sum([int(i) for i in list(isin_even)])
    odd_sum = sum([int(i) for i in list(isin_odd)])

    # calculate check digit
    mod = (even_sum + odd_sum) % 10
    check_digit_calc = 10 - mod

    if check_digit == check_digit_calc:
        return True
    else:
        return False
