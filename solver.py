import sys

import numpy as np

import util.constants as Constants
import util.file_util as File_Util


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
        for index, value in enumerate(result):
            print(f'x{index + 1} = {value}')
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')


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
        if round(value, 4) < 0:
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


def monta_vetor_de_retorno_simplex(tableau, resultado_dicionario, quantidade_de_variaveis):
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

    return monta_vetor_de_retorno_simplex(tableau, resultado_dicionario, quantidade_de_variaveis)


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


########################################################################################################################
########################################################################################################################
######################### ^^^^^^^^^ SIMPLEX ^^^^^^^^^ | vvvvvvvvvv SIMPLEX 2 FASES vvvvvvvvvv ##########################
########################################################################################################################
########################################################################################################################

def normalize_f_obj_simplex_2_fases(
        restr_A_normalizadas, restr_op, restr_b,
        quantidade_de_variaveis_original, quantidade_de_variaveis_de_folga, quantidade_de_variaveis_artificiais
):
    """
    Essa função realiza a normalização da função objetivo do problema
    :param restr_A_normalizadas: matriz A das restrições normalizadas
    :param restr_op: vetor contendo os símbolos de cada uma das restrições normalizadas, ou seja, na ordem correta
    :param restr_b: matriz b das restrições normalizadas
    :param quantidade_de_variaveis_original: quantidade original de variáveis do problema
    :param quantidade_de_variaveis_de_folga: quantidade de variáveis de folga criadas para o problema
    :param quantidade_de_variaveis_artificiais: quantidade de variáveis de artificiais criadas para o problema
    :return: f_obj - função objetivo normalizada, soma_func_obj - resultado da soma da função objetivo
    """
    f_obj = list()
    f_obj.extend([0] * quantidade_de_variaveis_original)
    f_obj.extend([0] * quantidade_de_variaveis_de_folga)
    f_obj.extend([-1] * quantidade_de_variaveis_artificiais)
    f_obj = np.array(f_obj)

    soma_func_obj = 0

    for index, restricao in enumerate(restr_A_normalizadas):
        if (restr_op[index] == Constants.equals_symbol) or (restr_op[index] == Constants.greater_or_equals_symbol):
            f_obj = f_obj + restricao
            soma_func_obj += restr_b[index]

    return f_obj, soma_func_obj


def normalize_f_obj_e_restr_A_simplex_2_fases(f_obj, restr_A, restr_op, restr_b):
    """
    Esta função realiza a normalização da função objetico e de cada uma das retrições do problema
    :param f_obj:    np.array float, contendo a função objetivo
    :param restr_A:  np.array float, contendo a matriz A das restrições
    :param restr_op: np.array string, contendo o vetor de operadores das restrições
    :param restr_b:  np.array float, contendo o vetor b das restrições
    :return: f_obj_normalizada np.array - função objetivo normalizada
           restr_A_normalizadas - matriz A de restrições normalizadas
           restr_b_ordenada - matriz b de restrições normalizadas
           soma_f_obj_normalizada - elemento [0][0] da matriz tableau
           quantidade_de_variaveis_de_folga - quantidade de variaveis de folga criadas para solucionar o problema
           quantidade_de_variaveis_artificiais - quantidade de variaveis artificiais criadas para solucionar o problema
    """
    quantidade_de_variaveis_original = len(f_obj)
    quantidade_de_variaveis_de_folga = len([
        op
        for op in restr_op
        if (op == Constants.greater_or_equals_symbol) or (op == Constants.less_or_equals_symbol)
    ])
    cont_auxiliar_variaveis_de_folga = 0
    quantidade_de_variaveis_artificiais = len([
        op
        for op in restr_op
        if (op == Constants.equals_symbol) or (op == Constants.greater_or_equals_symbol)
    ])
    cont_auxiliar_variaveis_artificiais = 0

    restr_A_ordenada = list()
    restr_b_ordenada = list()
    restr_op_ordenada = list()

    auxiliar_as_restr_A_ordenada = list()
    auxiliar_as_restr_b_ordenada = list()
    auxiliar_as_restr_op_ordenada = list()

    for index, restricao in enumerate(restr_A):
        if (restr_op[index] == Constants.equals_symbol) or (restr_op[index] == Constants.greater_or_equals_symbol):
            restr_A_ordenada.append(restricao)
            restr_b_ordenada.append(restr_b[index])
            restr_op_ordenada.append(restr_op[index])
        else:
            auxiliar_as_restr_A_ordenada.append(restricao)
            auxiliar_as_restr_b_ordenada.append(restr_b[index])
            auxiliar_as_restr_op_ordenada.append(restr_op[index])
    restr_A_ordenada.extend(auxiliar_as_restr_A_ordenada)
    restr_A_ordenada = np.array(restr_A_ordenada)

    restr_b_ordenada.extend(auxiliar_as_restr_b_ordenada)
    restr_b_ordenada = np.array(restr_b_ordenada)

    restr_op_ordenada.extend(auxiliar_as_restr_op_ordenada)
    restr_op_ordenada = np.array(restr_op_ordenada)

    restr_A_normalizadas = list()

    for index, restricao in enumerate(restr_A_ordenada):
        restricao = [valor for valor in restricao]
        restricao.extend([0] * (quantidade_de_variaveis_de_folga + quantidade_de_variaveis_artificiais))

        if restr_op[index] == Constants.greater_or_equals_symbol:
            restricao[quantidade_de_variaveis_original + cont_auxiliar_variaveis_de_folga] = -1
            cont_auxiliar_variaveis_de_folga += 1
        elif restr_op[index] == Constants.less_or_equals_symbol:
            restricao[quantidade_de_variaveis_original + cont_auxiliar_variaveis_de_folga] = +1
            cont_auxiliar_variaveis_de_folga += 1

        if (restr_op[index] == Constants.equals_symbol) or (restr_op[index] == Constants.greater_or_equals_symbol):
            restricao[-(quantidade_de_variaveis_artificiais - cont_auxiliar_variaveis_artificiais)] = 1
            cont_auxiliar_variaveis_artificiais += 1

        restr_A_normalizadas.append(np.array(restricao))

    restr_A_normalizadas = np.array(restr_A_normalizadas)
    f_obj_normalizada, soma_f_obj_normalizada = normalize_f_obj_simplex_2_fases(
        restr_A_normalizadas,
        restr_op_ordenada,
        restr_b_ordenada,
        quantidade_de_variaveis_original,
        quantidade_de_variaveis_de_folga,
        quantidade_de_variaveis_artificiais
    )

    return f_obj_normalizada, restr_A_normalizadas, restr_b_ordenada, soma_f_obj_normalizada, quantidade_de_variaveis_de_folga, quantidade_de_variaveis_artificiais


def mount_tableau_simplex_2_fases(f_obj_normalizada, soma_f_obj_normalizada, restr_A_normalizadas, restr_b):
    """
    Essa função realiza a montagem da matriz tableau
    :param f_obj_normalizada: função objetivo já formalizada
    :param soma_f_obj_normalizada: posição [0][0] da matriz tableau
    :param restr_A_normalizadas: matriz A das restrições normalizadas
    :param restr_b: matriz b das restrições normalizadas
    :return: matriz que representa o tableau
    """
    tableau = list()

    L0 = [soma_f_obj_normalizada]
    L0.extend(f_obj_normalizada)
    L0 = np.array(L0)
    L0 = L0 * (-1)
    tableau.append(L0)

    for index, restricao in enumerate(restr_A_normalizadas):
        linha = list()
        linha.append(restr_b[index])
        linha.extend(restricao)

        tableau.append(np.array(linha))

    return np.array(tableau)


def remove_variaveis_artificiais(tableau, quantidade_de_variaveis_artificiais):
    """
    Essa função realiza a geração de uma nova matriz tableau que não possui as variáveis artificiais. Essa matriz é
    a que se gera na segunda fase do simplex de 2 fases
    :param tableau: matriz tableau completa e já "resolvida", ou seja, com todas as iterações realizadas
    :param quantidade_de_variaveis_artificiais: quantidade de variáveis artificiais criadas para resolver o problema
    :return: nova matriz tableau que não possui as colunas das variáveis artificiais
    """
    novo_tableau = []
    for index, linha_original in enumerate(tableau):
        linha_copia = [valor for valor in linha_original]
        for vez in range(quantidade_de_variaveis_artificiais):
            linha_copia.pop()
        novo_tableau.append(np.array(linha_copia))

    return np.array(novo_tableau)


def monta_resultado_dicionario(tableau, quantidade_de_variaveis_artificiais):
    """
    Essa função realiza a montagem do dicionário resposta do problema. Vale salientar que o dicionário do simplex
    2 fases é diferente do simplex normal, aqui ele respeita o seguinte padrão: key -> value, onde a key é o index
    da linha e o value é o index da coluna que corresponde à variável
    :param tableau: matriz tableau já pronta
    :param quantidade_de_variaveis_artificiais: quantidade de variáveis artificiais geradas para resolver o problema
    :return: dicionário resposta contendo já a atribuição de algumas variáveis às linhas, tais variáveis não são base
    """
    resultado_dicionario = {}
    cont_quantidade_de_variaveis_artificiais = 0
    indexes_ja_alocados = []
    f_obj_copia = [valor for valor in tableau[0]]
    f_obj_copia.reverse()

    for index, linha in enumerate(tableau):
        if index == 0:
            continue

        if cont_quantidade_de_variaveis_artificiais == quantidade_de_variaveis_artificiais:
            for index_coluna, valor_coluna in enumerate(f_obj_copia):
                if index_coluna < quantidade_de_variaveis_artificiais:
                    continue
                if index_coluna == 0:
                    break
                if valor_coluna == 0:
                    resultado_dicionario[index] = len(f_obj_copia) - index_coluna - 1

        else:
            index_selecionado = len(tableau[0]) - (
                    quantidade_de_variaveis_artificiais - cont_quantidade_de_variaveis_artificiais
            )
            resultado_dicionario[index] = index_selecionado
            indexes_ja_alocados.append(index_selecionado)
            cont_quantidade_de_variaveis_artificiais += 1

    return resultado_dicionario


def copia_tableau(tableau):
    """
    Essa função realiza a cópia de uma matriz tableau
    :param tableau: matriz tableau a ser copiada
    :return: cópia da matriz tableau
    """
    tableau_copia = []
    for linha in tableau:
        tableau_copia.append(np.array([valor for valor in linha]))
    return np.array(tableau_copia)


def calcula_ultimo_escalonamento(tableau_2a_fase, f_obj):
    """
    Essa função realiza o último escalonamento do simplex 2 fases.
    :param tableau_2a_fase: matriz tableau da 2 fase do simplex 2 fases
    :param f_obj: função objetivo
    :return: matriz tableau com cada um dos resultados de cada variável
    """
    f_obj_copia = [valor for valor in f_obj]
    f_obj_copia.extend([0] * (len(tableau_2a_fase[0]) - len(f_obj)))
    tableau_copia = copia_tableau(tableau_2a_fase)
    tableau_copia[0] = tableau_copia[0] * 0
    tableau_copia[0] = tableau_copia[0] + np.array(f_obj_copia)

    indexes_para_zerar = []
    for index, valor in enumerate(f_obj[1:]):
        if valor != 0:
            indexes_para_zerar.append(index + 1)

    for index_para_zerar in indexes_para_zerar:
        index_linha = 1
        while tableau_copia[index_linha][index_para_zerar] == 0:
            index_linha += 1

        sinal = -1

        tableau_copia[0] = tableau_copia[0] + (
                (tableau_copia[0][index_para_zerar] * tableau_copia[index_linha]) * sinal
        )
    return tableau_copia


def monta_vetor_de_retorno_simplex_2_fases(tableau_2a_fase, resultado_dicionario, quantidade_de_variaveis_base):
    """
    Essa função monta o vetor de resposta para o problema de simplex 2 fases
    :param tableau_2a_fase: matriz tableau da segunda fase do simplex 2 fases
    :param resultado_dicionario: o dicionário que mostra qual linha está o valor de cada variável base
    :param quantidade_de_variaveis_base: quantidade de variáveis base do problema
    :return: vetor contendo os valores de cada uma das variáveis
    """
    vetor_resultado = list()
    variaveis_nao_nulas = [x for x in resultado_dicionario.values()]
    for x in range(1, quantidade_de_variaveis_base + 1):
        if x in variaveis_nao_nulas:
            index_linha = variaveis_nao_nulas.index(x) + 1
            vetor_resultado.append(tableau_2a_fase[index_linha][0])
        else:
            vetor_resultado.append(0)

    return vetor_resultado


def do_simplex_2_fases(f_obj_normalizada, soma_f_obj_normalizada, restr_A_normalizadas, restr_b,
                       quantidade_de_variaveis_artificiais, verbose):
    """
    Essa função realiza todos os processos necessários para a resolução do problema passado
    :param f_obj_normalizada: função objetivo normalizada
    :param soma_f_obj_normalizada: posição [0][0] da matiz tableau
    :param restr_A_normalizadas: lado A das restrições formatadas
    :param restr_b: lado B das restrições formatadas
    :param quantidade_de_variaveis_artificiais: quantidade de variáveis artificiais criadas para solucionar o problema
    :param verbose: flag para realizar o verbose, ou não
    :return: np.array() contendo o valor de cada variável
    """
    tableau = mount_tableau_simplex_2_fases(f_obj_normalizada, soma_f_obj_normalizada, restr_A_normalizadas, restr_b)
    quantidade_de_variaveis_base = len([valor for valor in tableau[0][1:] if valor != 0])
    resultado_dicionario = monta_resultado_dicionario(tableau, quantidade_de_variaveis_artificiais)

    do_verbose(verbose, tableau)

    # PRIMEIRA FASE DO TABLEAU
    while linha_possui_negativo(tableau[0]):
        index_coluna_pivo = get_index_com_menor_valor(tableau[0][1:]) + 1
        index_linha = get_index_linha(tableau, index_coluna_pivo) + 1

        resultado_dicionario[index_linha] = index_coluna_pivo

        escalona_linha(tableau, index_linha, index_coluna_pivo)
        escalona_resto_da_matriz(tableau, tableau[index_linha], index_linha, index_coluna_pivo)

        do_verbose(verbose, tableau)

    # SEGUNDA FASE DO PLATEAU
    tableau_2a_fase = remove_variaveis_artificiais(tableau, quantidade_de_variaveis_artificiais)
    do_verbose(verbose, tableau_2a_fase)
    tableau_2a_fase = calcula_ultimo_escalonamento(tableau_2a_fase, f_obj_normalizada[:len(tableau_2a_fase) + 1])
    # TODO verificar dicionario resposta e retornar o vetor correto
    return monta_vetor_de_retorno_simplex_2_fases(tableau_2a_fase, resultado_dicionario, quantidade_de_variaveis_base)


def solver(objet, f_obj, restr_A, restr_op, restr_b, verbose=False):
    """
    Função para solução de problemas de programação linear
    Deve ser implementada para solução de PPL usando métodos Simplex e Simplex Duas Fases.
    Não devem ser adicionados novos parâmetros à função.

    Parâmetros:
    :param objet:    string, contendo indicação de 'MA' (para maximização) ou 'MI' (para minimização)
    :param f_obj:    np.array float, contendo a função objetivo
    :param restr_A:  np.array float, contendo a matriz A das restrições
    :param restr_op: np.array string, contendo o vetor de operadores das restrições
    :param restr_b:  np.array float, contendo o vetor b das restrições
    :param verbose:  booleano opcional para impressão de valores intermediários (não obrigatório implementar)
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
    quantidade_de_variaveis_iniciais = len(f_obj)

    if is_simplex_base:
        quantidade_de_variaveis_de_folga = len(restr_A)
        return do_simplex(
            normalize_f_obj_simplex(objet, f_obj, quantidade_de_variaveis_de_folga),
            normalize_restr_A_simplex(restr_A),
            restr_b,
            quantidade_de_variaveis_iniciais,
            quantidade_de_variaveis_de_folga,
            verbose
        )
    else:
        f_obj_normalizada, restr_A_normalizadas, restr_b_ordenada, soma_f_obj_normalizada, \
        quantidade_de_novas_variaveis, quantidade_de_variaveis_artificiais = \
            normalize_f_obj_e_restr_A_simplex_2_fases(f_obj, restr_A, restr_op, restr_b)
        return do_simplex_2_fases(
            f_obj_normalizada,
            soma_f_obj_normalizada,
            restr_A_normalizadas,
            restr_b_ordenada,
            quantidade_de_variaveis_artificiais,
            verbose
        )


if __name__ == '__main__':
    main()
