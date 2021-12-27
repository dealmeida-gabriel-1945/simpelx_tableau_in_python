comment_char = "#"
space_char = " "

maximization_inititals = "MA"
minimization_inititals = "MI"
restrictions_inititals = "RE"
function_solution_initials = "SF"
variables_solution_initials = "SV"

equals_symbol = '=='
less_or_equals_symbol = '<='
greater_or_equals_symbol = '>='
possible_comparition_symbols = [
    equals_symbol,
    less_or_equals_symbol,
    greater_or_equals_symbol
]


def list_to_string(to_parse, separator=''):
    return separator.join(to_parse)


def non_empty_list_or_none(watched_list):
    return watched_list if len(watched_list) > 0 else None


def row_has_negative_element(row):
    negative_values = list(filter(lambda x: x < 0, row))
    return True if len(negative_values) > 0 else False

