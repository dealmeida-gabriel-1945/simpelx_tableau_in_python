import util.constants as Constants

"""
Essa classe representa cada problema
"""


class Problem:
    def __init__(self):
        self.is_minimization = None
        self.objective_function = list()
        self.restrictions = list()

    def retorna_vetor_A_das_restricoes(self):
        """
        Essa função retorna o lado A das restrições
        :return: matriz A das retrições, a qual contém os valores de cada restrição
        """
        return [restriction.left_side_values for restriction in self.restrictions]

    def retorna_vetor_b_das_restricoes(self):
        """
        Essa função retorna o lado b das restrições
        :return: matriz b das retrições, a qual contém os valores comparados de cada restrição
        """
        return [restriction.right_side_value for restriction in self.restrictions]

    def retorn_operacao_das_restricoes(self):
        """
        Essa função retorna as operações de comparação de cada uma das restrições
        :return: vetor contendo as operações de cada uma das restrições
        """
        return [restriction.comparition for restriction in self.restrictions]
