# -*- coding: utf-8 -*-
"""
======================================================================
 treinamento.py  -  AULA 02 (Aprendizado de Maquina)
----------------------------------------------------------------------
 Aqui ficam as funcoes que TREINAM os modelos dos 3 tipos de
 aprendizado vistos na aula:

   1. SUPERVISIONADO - Classificacao (aprovar credito)
   2. SUPERVISIONADO - Regressao (prever preco)
   3. NAO SUPERVISIONADO - Agrupamento (segmentar clientes / KMeans)
   4. POR REFORCO - exemplo simples de labirinto (sem matematica pesada)
======================================================================
"""
import numpy as np
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.cluster import KMeans


# ---------------------------------------------------------------------
# 1) SUPERVISIONADO - CLASSIFICACAO
# ---------------------------------------------------------------------
def treinar_classificacao(X_tr, y_tr):
    """Treina um classificador (Regressao Logistica).
    Apesar do nome, ela CLASSIFICA: responde 'sim/nao', '0/1'.
    Ex.: o credito sera aprovado (1) ou negado (0)?"""
    modelo = LogisticRegression(max_iter=1000, random_state=42)
    modelo.fit(X_tr, y_tr)   # .fit() = "aprender com os exemplos"
    print("[OK] Classificador treinado (Regressao Logistica)")
    return modelo


# ---------------------------------------------------------------------
# 2) SUPERVISIONADO - REGRESSAO
# ---------------------------------------------------------------------
def treinar_regressao(X_tr, y_tr):
    """Treina um modelo de Regressao Linear.
    Regressao preve um NUMERO continuo (ex.: preco de um imovel)."""
    modelo = LinearRegression()
    modelo.fit(X_tr, y_tr)
    print("[OK] Regressor treinado (Regressao Linear)")
    return modelo


# ---------------------------------------------------------------------
# 3) NAO SUPERVISIONADO - AGRUPAMENTO (KMeans)
# ---------------------------------------------------------------------
def treinar_agrupamento(X, n_grupos=3):
    """Agrupa clientes parecidos SEM rotulos (nao supervisionado).
    O KMeans descobre sozinho 'n_grupos' grupos (clusters).
    Ex.: separar clientes em 3 perfis de consumo."""
    modelo = KMeans(n_clusters=n_grupos, random_state=42, n_init=10)
    grupos = modelo.fit_predict(X)   # diz a qual grupo cada cliente pertence
    print(f"[OK] KMeans treinado: {n_grupos} grupos encontrados")
    return modelo, grupos


# ---------------------------------------------------------------------
# 4) POR REFORCO - LABIRINTO SIMPLES (didatico, sem matematica pesada)
# ---------------------------------------------------------------------
def treinar_reforco_labirinto(episodios=200):
    """Exemplo MINIMO de Aprendizado por Reforco (Q-Learning).

    Cenario: um corredor com 5 posicoes [0,1,2,3,4].
      - O agente comeca na posicao 0.
      - O objetivo (recompensa +1) esta na posicao 4.
      - Acoes possiveis: 0 = esquerda, 1 = direita.
      - Penalidade pequena (-0.01) a cada passo para incentivar rapidez.

    O agente NAO sabe nada no inicio. Ele aprende por TENTATIVA E ERRO,
    guardando numa 'tabela Q' o quao boa e' cada acao em cada posicao."""
    n_estados, n_acoes = 5, 2
    Q = np.zeros((n_estados, n_acoes))   # tabela de conhecimento (comeca zerada)
    alpha, gamma, epsilon = 0.1, 0.9, 0.2  # taxa de aprend., desconto, exploracao

    for _ in range(episodios):
        estado = 0
        for _ in range(20):                      # limite de passos por tentativa
            # decide: explorar (acao aleatoria) ou usar o que ja sabe
            if np.random.rand() < epsilon:
                acao = np.random.randint(n_acoes)
            else:
                acao = int(np.argmax(Q[estado]))
            # aplica a acao no ambiente
            novo = max(0, estado - 1) if acao == 0 else min(4, estado + 1)
            recompensa = 1.0 if novo == 4 else -0.01
            # atualiza o conhecimento (formula do Q-Learning)
            Q[estado, acao] += alpha * (
                recompensa + gamma * np.max(Q[novo]) - Q[estado, acao]
            )
            estado = novo
            if estado == 4:                      # chegou ao objetivo
                break

    # politica final: melhor acao aprendida para cada posicao
    politica = ["direita" if np.argmax(Q[s]) == 1 else "esquerda" for s in range(n_estados)]
    print("[OK] Agente treinado no labirinto por reforco")
    return Q, politica


if __name__ == "__main__":
    print(">> Demonstrando o Aprendizado por Reforco (labirinto)\n")
    Q, politica = treinar_reforco_labirinto()
    print("Tabela Q aprendida (linhas = posicoes, colunas = [esq, dir]):")
    print(np.round(Q, 2))
    print("\nMelhor acao em cada posicao:")
    for i, a in enumerate(politica):
        print(f"   posicao {i} -> ir para {a}")
