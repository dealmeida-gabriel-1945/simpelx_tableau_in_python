import util.constants as Constants
import numpy as np
import sys
import util.file_util as File_Util
import scipy.optimize as opt


def main():
    problems = None
    verbose = None
    if len(sys.argv) <= 1:
        problems = File_Util.get_problems_from_file(
            '/home/gabriel/Documents/projects/python/simplex_solver/examples/problemas.txt')
        verbose = True
    else:
        problems = File_Util.get_problems_from_file(sys.argv[1])
        verbose = Constants.verbose_param in sys.argv

    for problem in problems:
        result = solver(
            Constants.minimization_inititals if problem.is_minimization else Constants.maximization_inititals,
            np.array(problem.objective_function),
            np.array(problem.get_left_side_restriction_matrix()),
            np.array(problem.get_comparition_restriction_list()),
            np.array(problem.get_right_side_restriction_matrix()),
            verbose=verbose
        )
        print(f'z = {result[0]}')
        for index, value in enumerate(result[1]):
            print(f'x{index + 1} = {value}')
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')


def normalize_restr_A_simplex(restr_A_original):
    restr_A = list()

    i = 0
    for restricao in restr_A_original:
        aux = [value for value in restricao]
        aux_loose = [0] * len(restr_A_original)
        aux_loose[i] = 1
        aux.extend(aux_loose)
        restr_A.append(np.array(aux))
        i += 1

    return np.array(restr_A)


def mount_tableau(f_obj, restr_A, restr_b):
    linhas = list()
    L0 = list()
    L0.append(0)
    for value in f_obj:
        L0.append((-1) * value)
    linhas.append(np.array(L0))

    for index, restricao in enumerate(restr_A):
        Ln = list()
        Ln.append(restr_b[index])
        Ln.extend(restricao)
        linhas.append(np.array([value for value in Ln]))

    return np.array(linhas)


def linha_possui_negativo(valores_base):
    for value in valores_base:
        if value < 0:
            return True
    return False


def get_index_com_menor_valor(valores_base, nao_negativo=False):
    menor_valor = None
    index_menor_valor = None
    for index, valor in enumerate(valores_base):
        if valor != 0:
            menor_valor = valor
            index_menor_valor = index
            break
    for index, valor in enumerate(valores_base):
        if nao_negativo:
            if (valor > 0) and (valor < menor_valor):
                menor_valor = valor
                index_menor_valor = index
        else:
            if (valor != 0) and (valor < menor_valor):
                menor_valor = valor
                index_menor_valor = index
    return index_menor_valor


def get_index_linha(tableau, index_coluna_pivo):
    resultado_divisoes = list()
    index_linha = 1
    while index_linha < len(tableau):
        if tableau[index_linha][index_coluna_pivo] == 0:
            divisao = Constants.comment_char
        else:
            divisao = tableau[index_linha][0] / tableau[index_linha][index_coluna_pivo]
        resultado_divisoes.append(divisao)
        index_linha += 1

    soma = 0
    for valor in resultado_divisoes:
        if valor != Constants.comment_char:
            soma += valor * (-1 if valor < 0 else +1)

    for index, valor in enumerate(resultado_divisoes):
        if valor == Constants.comment_char:
            resultado_divisoes[index] = soma

    return get_index_com_menor_valor(resultado_divisoes, nao_negativo=True)


def escalona_linha(tableau, index_linha, index_coluna_pivo):
    tableau[index_linha] = tableau[index_linha] / tableau[index_linha][index_coluna_pivo]


def pega_proxima_linha_a_ter_coluna_anulada(tableau, index_linha, index_coluna_pivo):
    i = 0
    while i < len(tableau):
        if (i != index_linha) and (tableau[i][index_coluna_pivo] != 0):
            return i
        i += 1
    return None


def escalona_resto_da_matriz(tableau, linha_a_ser_escalonada_original, index_linha, index_coluna_pivo):
    index_proxima_linha_a_anular_coluna = pega_proxima_linha_a_ter_coluna_anulada(
        tableau, index_linha, index_coluna_pivo
    )
    while index_proxima_linha_a_anular_coluna is not None:

        linha_a_ser_mudada = tableau[index_proxima_linha_a_anular_coluna]

        valor_1 = linha_a_ser_escalonada_original[index_coluna_pivo]
        valor_2 = linha_a_ser_mudada[index_coluna_pivo]

        valor_2 *= -1

        tableau[index_proxima_linha_a_anular_coluna] = (
           linha_a_ser_escalonada_original * valor_2
        ) + (
           linha_a_ser_mudada * valor_1
        )

        index_proxima_linha_a_anular_coluna = pega_proxima_linha_a_ter_coluna_anulada(
            tableau, index_linha, index_coluna_pivo
        )


def monta_vetor_de_retorno(tableau, resultado_dicionario, quantidade_de_variaveis):
    cont = 1
    resultados = list()
    while cont <= quantidade_de_variaveis:
        if cont in resultado_dicionario:
            resultados.append(tableau[resultado_dicionario[cont]][0])
        else:
            resultados.append(0)
        cont += 1
    return [tableau[0][0], resultados]


def do_verbose(verbose, tableau):
    if verbose:
        print(tableau)


def do_simplex(f_obj, restr_A, restr_b, quantidade_de_variaveis, quantidade_de_variaveis_de_folga, verbose=False):
    resultado_dicionario = {}
    tableau = mount_tableau(f_obj, restr_A, restr_b)
    valores_base = tableau[0][1:quantidade_de_variaveis_de_folga + 1]

    do_verbose(verbose, tableau)

    while linha_possui_negativo(valores_base):
        index_coluna_pivo = get_index_com_menor_valor(valores_base) + 1
        index_linha = get_index_linha(tableau, index_coluna_pivo) + 1

        linha_a_ser_escalonada_original = tableau[index_linha]

        resultado_dicionario[index_coluna_pivo] = index_linha

        escalona_linha(tableau, index_linha, index_coluna_pivo)
        escalona_resto_da_matriz(tableau, linha_a_ser_escalonada_original, index_linha, index_coluna_pivo)

        do_verbose(verbose, tableau)

    return monta_vetor_de_retorno(tableau, resultado_dicionario, quantidade_de_variaveis)


def normalize_f_obj_simplex(objet, f_obj, number_of_loose):
    aux = [value for value in f_obj]
    aux.extend([0] * number_of_loose)
    if objet == Constants.maximization_inititals:
        return np.array(aux)
    return np.array([value * (-1) for value in aux])


def solver(objet, f_obj, restr_A, restr_op, restr_b, verbose=False):
    """
    Função para solução de problemas de programação linear
    Deve ser implementada para solução de PPL usando métodos Simplex e Simplex Duas Fases.
    Não devem ser adicionados novos parâmetros à função.

    Parâmetros:
    : param objet:    string, contendo indicação de 'MA' (para maximização) ou 'MI' (para minimização)
    : param f_obj:    np.array float, contendo a função objetivo
    : param restr_A:  np.array float, contendo a matriz A das restrições
    : param restr_op: np.array string, contendo o vetor de operadores das restrições
    : param restr_b:  np.array float, contendo o vetor b das restrições
    : param verbose:  booleano opcional para impressão de valores intermediários (não obrigatório implementar)
    : return:         np.array contendo os valores das variáveis (não retornar valor da função objetivo nem variáveis de folga)
    """

    # verifica tipo dos parâmetros (não remover)
    if not isinstance(objet, str):
        raise TypeError('Parâmetro "objet" diferente do especificado.')

    if (objet != 'MA' and objet != 'MI'):
        raise TypeError('Tipo de objetivo diferente do especificado.')

    if not isinstance(f_obj, np.ndarray):
        raise TypeError('Parâmetro "f_obj" diferente do especificado.')

    if not isinstance(restr_A, np.ndarray):
        raise TypeError('Parâmetro "restr_A" diferente do especificado.')

    if not isinstance(restr_op, np.ndarray):
        raise TypeError('Parâmetro "restr_op" diferente do especificado.')

    if not isinstance(restr_b, np.ndarray):
        raise TypeError('Parâmetro "restr_b" diferente do especificado.')

    #################################################################
    ##
    # implemente seu código aqui
    # caso queira, subdivida o código em funções
    ##
    #################################################################

    is_simplex_base = all([op == Constants.less_or_equals_symbol for op in restr_op])
    quantidade_de_variaveis = len(f_obj)
    quantidade_de_variaveis_de_folga = len(restr_A)
    if is_simplex_base:
        return do_simplex(
            normalize_f_obj_simplex(objet, f_obj, quantidade_de_variaveis_de_folga),
            normalize_restr_A_simplex(restr_A),
            restr_b,
            quantidade_de_variaveis,
            quantidade_de_variaveis_de_folga,
            verbose
        )
    else:
        print('SIMPLEX 2 FASES')


if __name__ == '__main__':
    main()
