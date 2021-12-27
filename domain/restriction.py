import util.constants as Constants


class Restriction:
    def __init__(self):
        self.left_side_values = list()
        self.comparition = None
        self.right_side_value = None

    def __str__(self):
        left_side = Constants.list_to_string(self.left_side_values, separator=Constants.space_char)
        return f'{left_side} {self.comparition} {self.right_side_value}'
