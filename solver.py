import util.constants as Constants
import numpy as np
import sys
import util.file_util as File_Util
import scipy.optimize as opt


def main():
    """
    Esse método é o main, ele apenas chama os métodos de leitura do arquivo e de resolução dos problemas, passando os
    parâmetros corretos de acordo com o modo de execução (por terminal ou por execução pela ide pycharm)
    :return: void
    """
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
        for index, value in enumerate(result[1]):
            print(f'x{index + 1} = {value}')
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')


########################################################################################################################
########################################################################################################################
######################### vvvvvvvvvv SIMPLEX vvvvvvvvvv | ^^^^^^^^^ SIMPLEX 2 FASES ^^^^^^^^^ ##########################
########################################################################################################################
########################################################################################################################

def normalize_restr_A_simplex(restr_A_original):
    """
    Essa função normaliza uma restrição de sinal <=
    :param restr_A_original: np.array() contendo os valores que "acompanham" cada x da restrição
    :return: np.array() contendo a restrição normalizada
    """
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


def mount_tableau_simplex(f_obj, restr_A, restr_b):
    """
    Essa função monta a matrix tableau
    :param f_obj: np.array() contendo a função objetivo normalizada
    :param restr_A: np.array() contendo cada restrição normalizada
    :param restr_b: np.array() contendo o lado direito de cada restrição
    :return: np.array() contendo cada uma das linhas da tabela tableau
    """
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
    """
    Essa função verifica se há valores negativos no vetor passado
    :param valores_base: vetor que contém os valores a serem analisados
    :return: bool, True -> possui valor negativo; False -> não possui valor negativo
    """
    for value in valores_base:
        if value < 0:
            return True
    return False


def get_index_com_menor_valor(valores_base, nao_negativo=False):
    """
    Pega o index com o menor valor, podendo ele ser menor negativo ou não
    :param valores_base: np.array() contendo os valores a serem analisados
    :param nao_negativo: bool, flag para permitir a análise de números negativo ou não (True/False)
    :return: long, index do menor valor no parâmetro "valores_base"
    """
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
    """
    Esse método realiza o processo de verificação de qual linha do tableau deverá ser utilizada juntamente com a coluna
    pivô
    :param tableau: np.array() matriz contendo todos os valores do problema simplex
    :param index_coluna_pivo: long, valor do index da coluna pivô
    :return: long index da linha do tableau deverá ser utilizada juntamente com a coluna pivô
    """
    resultado_divisoes = list()
    index_linha = 1
    while index_linha < len(tableau):
        if tableau[index_linha][index_coluna_pivo] == 0:
            divisao = Constants.comment_char
        else:
            divisao = tableau[index_linha][0] / tableau[index_linha][index_coluna_pivo]
        resultado_divisoes.append(divisao)
        index_linha += 1

    # Às vezes pode ocorre de que tableau[index_linha][index_coluna_pivo] adiquira um valor nulo (0)
    # quando isso acontecer, em vez de colocar zero no vetor de resultados das divisões, colocarmos '#'
    # para posteriormente trocá-los pela (soma + 100) do módulo de todos os outros valores
    soma = 0
    for valor in resultado_divisoes:
        if valor != Constants.comment_char:
            soma += valor * (-1 if valor < 0 else +1)

    for index, valor in enumerate(resultado_divisoes):
        if valor == Constants.comment_char:
            resultado_divisoes[index] = soma + 100

    return get_index_com_menor_valor(resultado_divisoes, nao_negativo=True)


def escalona_linha(tableau, index_linha, index_coluna_pivo):
    """
    Esse método divide toda a linha pelo elemento pivô
    :param tableau: np.array() matriz contendo todos os valores do problema simplex
    :param index_linha: long, valor do index da linha a ser dividida
    :param index_coluna_pivo: long, valor do index da coluna pivô
    :return: void
    """
    tableau[index_linha] = tableau[index_linha] / tableau[index_linha][index_coluna_pivo]


def pega_proxima_linha_a_ter_coluna_anulada(tableau, index_linha, index_coluna_pivo):
    """
    Retornao index da proxima linha que, na coluna "index_coluna_pivo", não possui um valor igual a 0
    :param tableau: np.array() matriz contendo todos os valores do problema simplex
    :param index_linha: long, valor do index da linha a ser ignorada
    :param index_coluna_pivo: long, valor do index da coluna pivô
    :return: long -> quando há mais linhas a serem trabalhadas; None -> quando não há mais linhas a serem trabalhadas
    """
    i = 0
    while i < len(tableau):
        if (i != index_linha) and (tableau[i][index_coluna_pivo] != 0):
            return i
        i += 1
    return None


def escalona_resto_da_matriz(tableau, linha_a_ser_escalonada_original, index_linha, index_coluna_pivo):
    """
    Essa função pega a proxima linha que, na coluna "index_coluna_pivo", não possui um valor igual a 0 e o faz tornar
    zero
    :param tableau: np.array() matriz contendo todos os valores do problema simplex
    :param linha_a_ser_escalonada_original:
    :param index_linha: long, valor do index da linha a ser ignorada
    :param index_coluna_pivo: long, valor do index da coluna pivô
    :return: void
    """
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
    """
    Essa função monta o vetor de retorno quando o problema simplex foi resolvido
    :param tableau: np.array() matriz contendo todos os valores do problema simplex
    :param resultado_dicionario: dicionário com as chaves equivalentes a ordem do x (x1 -> 1; x2 -> 2; x3 -> 2; etc...)
    e os valores equivalente às linhas que eles "estão"
    :param quantidade_de_variaveis_de_folga: long quantidade de variáveis de folga criadas para o problema
    :return: np.array() a posição 0 é o valor de Z, a segunda é um np.array() contendo o valor de cada variável
    """
    cont = 1
    resultados = list()
    while cont <= quantidade_de_variaveis:
        if cont in resultado_dicionario:
            resultados.append(tableau[resultado_dicionario[cont]][0])
        else:
            resultados.append(0)
        cont += 1
    return np.array(resultados)


def do_verbose(verbose, tableau):
    """
    Essa função realiza o verbose
    :param verbose: flag para realizar o verbose ou não
    :param tableau: np.array() matriz contendo todos os valores do problema simplex
    :return: void
    """
    if verbose:
        print(tableau)


def do_simplex(f_obj, restr_A, restr_b, quantidade_de_variaveis, quantidade_de_variaveis_de_folga, verbose=False):
    """
    Essa função realiza o processo de resolução do problem de simplex

    :param f_obj: np.array() que contém os valores que "acompanham" cada x na função objetivo
    :param restr_A: np.array() que contém os vetores que contêm os valores que "acompanham" cada x das restrições
    :param restr_b: np.array() que contém os valores que do lado direito de cada restrição
    :param quantidade_de_variaveis: long quantidade de variáveis normais que a função objetivo possui
    :param quantidade_de_variaveis_de_folga: long quantidade de variáveis de folga criadas para o problema
    :param verbose: bool flag para informar se haverá verbose ou não
    :return: np.array() contendo o valor de cada variável
    """
    resultado_dicionario = {}
    tableau = mount_tableau_simplex(f_obj, restr_A, restr_b)
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


def normalize_f_obj_simplex(objet, f_obj, numero_de_variveis_de_folga):
    """
    Essa função normaliza a função objetivo para resolver o simplex
    :param objet: String 'MA' ou 'MI'
    :param f_obj: np.array() função objetivo
    :param numero_de_variveis_de_folga: quantidade de variáveis de folga necessárias
    :return: np.array() cotendo a função objetivo normalizada
    """
    aux = [value for value in f_obj]
    aux.extend([0] * numero_de_variveis_de_folga)
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

    # Verificação se o problema é simplex ou simplex 2 fases
    is_simplex_base = all([op == Constants.less_or_equals_symbol for op in restr_op])

    if is_simplex_base:
        quantidade_de_variaveis = len(f_obj)
        quantidade_de_variaveis_de_folga = len(restr_A)
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
