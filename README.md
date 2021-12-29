[//]: # (Título e Descrição)
![](docs/images/01_ifmg_formiga_logo.png)
# IFMG - campus Formiga
# Trabalho de Pesquisa Operacional
## Resolução de problemas com Simplex e Simplex 2 fases

### Professor: Felipe Augusto Lima Reis

### Aluno: Gabriel Guimarães de Almeida

### Data de conclusão: 28/12/2021

------------------------------------------------------------

[//]: # (Tabela de Conteúdos)
<!--ts-->
* [Enunciado do trabalho](#enunciado-do-trabalho)
* [Requisitos](#requisitos)
* [Como executar o algoritmo](#como-executar-o-algoritmo)
  * [Como executar seus próprios problemas Simplex](#como-executar-seus-próprios-problemas-simplex)
* [Tecnologia e materiais utilizados](#tecnologia-e-materiais-utilizados)
* [Estrutura de pastas](#estrutura-de-pastas)
<!--te-->

------------------------------------------------------------

Enunciado do trabalho
=========
Para saber mais sobre o enunciado do trabalho verifique o arquivo **docs/po_trabalho_simplex.pdf**

Requisitos
=========
* [Python 3](https://docs.python.org/3/) - linguagem obrigatória para o trabalho
* [pip](https://pip.pypa.io/en/stable/) - instalador de pacotes python. A versão utilizada é a 20.0.2

Como executar o algoritmo
=========
Há duas formas testadas para a execução do algoritmo desenvolvido, um é pelo *run* da IDE PyCharm e outro por linha de 
comando, a qual deve seguir o seguinte padrão:
>python3 solver.py "path para o arquivo contendo as problemas" [-v]

* -v é uma *flag* que o usuário pode utilizar para obrigar o algoritmo a mostrar cada estado que a matriz tableau de
problema passa

Como executar seus próprios problemas Simplex
=========
Para adicionar seus próprios problemas Simplex, você deve criar um arquivo .txt e dentro adicionar um problema por 
linha. Exemplo:

Tenha o problema

>min z = 50 x1 + 45 x2 + 55 x3
> 
> suj. a
> 
> 4 x1 + 2 x2 + 2 x3 >= 35
> 
> 5 x1 + 6 x2 + 5 x3 <= 80
> 
> 1 x1 + 5 x2 + 2 x3 >= 20
> 
> x1, x2, x3 >= 0
 
Você deve adicionálo da seguinte forma no arquivo .txt:

>MI[50 45 55] RE[4 2 2 >= 35], [5 6 5 <= 80], [1 5 2 >= 20] SF[0] SV[0 0 0]

* **MI** quer dizer "minimização", caso deseje maximização, use MA
* **RE** representa os vetores correspondentes à cada uma das restrições
  * Os sinais possíveis para as restrições são: **>= <= ==** 
* **SF** representa o valor esperado para a função objetivo, caso não saiba o que esperar, coloque zero :) 
* **SV** representa os valorres esperados para cada uma das variáveis, caso não saiba o que esperar, coloque zeros :)
* **!!!Atenção!!!**
  * Caso você queira adicionar mais de um problema por arquivo, não há problema. Mas respeite a regra de um problema por
linha!
  * Caso você queira adicionar anotações no arquivo de problemas, coloque **#** no início da linha, tal caractere
faz o algoritmo ignorar a linha

Tecnologia e materiais utilizados
=========

* [Python 3](https://docs.python.org/3/) - linguagem obrigatória para o trabalho
* [pip](https://pip.pypa.io/en/stable/) - instalador de pacotes python. A versão utilizada é a 20.0.2
* [Numpy e SciPy](https://docs.scipy.org/doc/) - pacotes bem difundidos na comunidade acadêmica por proporcionar grande
facilidade ao se trabalhar com operações entre matrizes e vetores 
* [git](https://git-scm.com/doc) - ferramenta de versionamento utilizada para gerenciar as versões do projeto
* [PyCharm](https://www.jetbrains.com/pt-br/pycharm/download/) - IDE da epresa *Jetbrains* que proporciona uma enorme 
gama de facilitadores na hora de codificar
* Gavações das aulas de Simplex e Simplex 2 fases realizadas pelo professor
* Resolução das listas de exercícios do professor

Estrutura de pastas
=========
Foi decidido a fragmentação das responsabilidades em arquivos python, os quais estão alocados em diferentes pastas
para uma melhor navegação. Cada pasta/arquivo e suas responsabilidades se encontram abaixo:

* *docs/* -> pasta para armazenamento de arquivos para a documentação do projeto
  * */images* -> pasta para armazenamento de arquivos de imagens para a documentação do projeto
  * *po_trabalho_simplex.pdf* -> arquivo .pdf contendo o enunciado do trabalho
* */domain* -> pasta que armazena algumas classes python, as quais representam os problemas e suas restrições
* */examples* -> pasta que armazena os arquivos de texto que contém os problemas que serão resolvidos pelo algoritmo
* */util* -> pasta que armazena arquivos python, os quais contêm funções úteis para a leitura dos arquivos de texto
e algumas constantes que são usadas ao longo do código