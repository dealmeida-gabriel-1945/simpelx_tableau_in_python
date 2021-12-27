from domain.problem import Problem
from domain.restriction import Restriction
import util.constants as Constants


def get_objective_funcion_mode(problem_part):
    if problem_part.startswith(Constants.maximization_inititals):
        return False
    elif problem_part.startswith(Constants.minimization_inititals):
        return True
    else:
        raise Exception(f'Function initials must be equals to '
                        f'{Constants.minimization_inititals} or '
                        f'{Constants.maximization_inititals}.')


def get_objective_funcion(problem_part, is_minimization):
    problem_part_copy = f'{problem_part}'
    problem_part_copy = problem_part_copy.split(
        f'{Constants.minimization_inititals if is_minimization else Constants.maximization_inititals}['
    )
    problem_part_copy = Constants.list_to_string(problem_part_copy)
    problem_part_copy = problem_part_copy.split(Constants.space_char)
    return [float(part) for part in problem_part_copy]


def get_restrictions(problem_parts, index_watched):
    str_to_split = f' {Constants.restrictions_inititals}['
    str_to_split_alt = f', ['
    problem_part_copy = problem_parts[index_watched]

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
        index_watched += 1
        problem_part_copy = problem_parts[index_watched]

    return  restrictions


def get_problems_from_file(file_name):
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
            problem.is_minimization = get_objective_funcion_mode(problem_parts[index_watched])

            # getting the objective funcion
            problem.objective_function = get_objective_funcion(problem_parts[index_watched], problem.is_minimization)

            index_watched += 1

            problem.restrictions = get_restrictions(problem_parts, index_watched)

            problems.append(problem)
        # Close the file
        f.close()
    return problems
