from domain.problem import Problem
from domain.restriction import Restriction
import util.constants as Constants

"""
Esse arquivo armazena uma série de funções que realizam a leitura dos arquivos de texto que possuem os problemas a serem
resolvidos pelo algoritmo
"""


def verifica_se_problema_eh_minimizacao(parte_do_problema):
    """
    Essa função realiza a verificação de se o problema tratado é de minimização.
    :param parte_do_problema: linha completa do problema
    :return: bool, True -> é minimização; False -> é maximização
    """
    if parte_do_problema.startswith(Constants.maximization_inititals):
        return False
    elif parte_do_problema.startswith(Constants.minimization_inititals):
        return True
    else:
        raise Exception(f'O verbo da função deve ser '
                        f'{Constants.minimization_inititals} ou '
                        f'{Constants.maximization_inititals}.')


def retorna_funcao_objetivo(linha_do_problema, eh_minimizacao):
    """
    Essa função retorna a função objetivo do problema
    :param linha_do_problema: linha do problema
    :param eh_minimizacao: flag que indica se o problema é de minimização ou não
    :return: vetor com os valores da função objetivo
    """
    problem_part_copy = f'{linha_do_problema}'
    problem_part_copy = problem_part_copy.split(
        f'{Constants.minimization_inititals if eh_minimizacao else Constants.maximization_inititals}['
    )
    problem_part_copy = Constants.list_to_string(problem_part_copy)
    problem_part_copy = problem_part_copy.split(Constants.space_char)
    return [float(part) for part in problem_part_copy]


def retorna_restricoes(linha_do_problema, indice_vizualizado):
    """
    Essa função retorna cada uma das restrições presentes no problema atual
    :param linha_do_problema: linha do problema
    :param indice_vizualizado: índice da restrição atual
    :return: vetor contendo vários outro vetores, os quais contêm os valores das restrições
    """
    str_to_split = f' {Constants.restrictions_inititals}['
    str_to_split_alt = f', ['
    problem_part_copy = linha_do_problema[indice_vizualizado]

    if not problem_part_copy.startswith(str_to_split):
        raise Exception(f'You need to specify the restrictions with {Constants.restrictions_inititals}.')

    restrictions = list()
    while not problem_part_copy.startswith(f' {Constants.function_solution_initials}'):
        restriction = Restriction()
        if problem_part_copy.startswith(str_to_split):
            problem_part_copy = Constants.list_to_string(problem_part_copy.split(str_to_split))
        else:
            problem_part_copy = Constants.list_to_string(problem_part_copy.split(str_to_split_alt))
        problem_part_copy = problem_part_copy.split(Constants.space_char)

        passed_comparition_symbol = False
        for part in problem_part_copy:
            if part in Constants.possible_comparition_symbols:
                restriction.comparition = part
                passed_comparition_symbol = True
            else:
                if passed_comparition_symbol:
                    restriction.right_side_value = float(part)
                else:
                    restriction.left_side_values.append(float(part))
        restrictions.append(restriction)
        indice_vizualizado += 1
        problem_part_copy = linha_do_problema[indice_vizualizado]

    return restrictions


def retorn_problemas_do_arquivo(file_name):
    """
    Essa função retira os problemas de um arquivo e os transforma em objetos python
    :param file_name: path para o arquivo
    :return: lista de objetos dos problemas
    """
    problems = list()

    with open(file_name) as f:
        lines = f.readlines()
        # Each line is analyzed to see if it contains useful information
        for line in lines:

            if line.startswith(Constants.comment_char):
                continue

            index_watched = 0
            problem = Problem()
            problem_parts = line.split("]")

            # getting the objective funcion mode
            problem.is_minimization = verifica_se_problema_eh_minimizacao(problem_parts[index_watched])

            # getting the objective funcion
            problem.objective_function = retorna_funcao_objetivo(problem_parts[index_watched], problem.is_minimization)

            index_watched += 1

            problem.restrictions = retorna_restricoes(problem_parts, index_watched)

            problems.append(problem)
        # Close the file
        f.close()
    return problems
