import util.constants as Constants

class Problem:
    def __init__(self):
        self.is_minimization = None
        self.objective_function = list()
        self.restrictions = list()

    def get_left_side_restriction_matrix(self):
        return [restriction.left_side_values for restriction in self.restrictions]

    def get_right_side_restriction_matrix(self):
        return [restriction.right_side_value for restriction in self.restrictions]

    def get_comparition_restriction_list(self):
        return [restriction.comparition for restriction in self.restrictions]

    def normalize(self):
        if not self.is_minimization:
            self.objective_function = [((-1) * value) for value in self.objective_function]

        for restriction in self.restrictions:
            if restriction.comparition == Constants.greater_or_equals_symbol:
                restriction.comparition = Constants.greater_or_equals_symbol
                restriction.left_side_values = [((-1) * value) for value in restriction.left_side_values]
                restriction.right_side_value = (-1) * restriction.right_side_value
