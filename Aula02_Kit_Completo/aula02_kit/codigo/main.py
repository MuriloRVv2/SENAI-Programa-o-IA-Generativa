# -*- coding: utf-8 -*-
"""
======================================================================
 main.py  -  AULA 02 (Aprendizado de Maquina) - PROJETO COMPLETO
----------------------------------------------------------------------
 Este e' o arquivo PRINCIPAL. Ele junta tudo e roda os 3 tipos de
 aprendizado de ponta a ponta:

   PARTE A - Classificacao (supervisionado)  -> aprovar credito
   PARTE B - Regressao    (supervisionado)   -> prever preco de imovel
   PARTE C - Agrupamento  (nao supervisionado)-> segmentar clientes
   PARTE D - Reforco      (Q-Learning)        -> labirinto simples

 COMO EXECUTAR:
   1) (opcional) python gerar_dados.py      # cria os CSV de exemplo
   2) python main.py                        # roda o projeto completo
======================================================================
"""
import preprocessamento as prep
import treinamento as tr
import avaliacao as av


def parte_A_classificacao():
    print("\n" + "=" * 60)
    print(" PARTE A - CLASSIFICACAO: aprovar ou negar credito")
    print("=" * 60)
    df = prep.carregar_csv("classificacao.csv")
    df = prep.tratar_faltantes(df)
    df = prep.codificar_categoricas(df)
    X, y = prep.separar_X_y(df, "aprovado")
    X_tr, X_te, y_tr, y_te = prep.dividir_treino_teste(X, y)
    X_tr_n, X_te_n, scaler = prep.normalizar(X_tr, X_te)

    modelo = tr.treinar_classificacao(X_tr_n, y_tr)
    av.avaliar_classificacao(modelo, X_te_n, y_te)

    # PREDICAO em um cliente novo (exemplo de uso real).
    # Reaproveitamos o MESMO scaler do treino (boa pratica).
    import pandas as pd
    novo = pd.DataFrame([{
        "idade": 35, "renda_mil": 9.0, "dividas_mil": 2.0,
        "anos_emprego": 8, "tem_imovel_sim": 1
    }])[X.columns]                       # garante a mesma ordem de colunas
    novo_norm = scaler.transform(novo)
    pred = modelo.predict(novo_norm)
    print(f"\n  >> Predicao para cliente novo: "
          f"{'APROVADO' if pred[0] == 1 else 'NEGADO'}")


def parte_B_regressao():
    print("\n" + "=" * 60)
    print(" PARTE B - REGRESSAO: prever preco de imovel")
    print("=" * 60)
    df = prep.carregar_csv("vendas.csv")
    df = prep.tratar_faltantes(df)
    X, y = prep.separar_X_y(df, "preco_mil")
    X_tr, X_te, y_tr, y_te = prep.dividir_treino_teste(X, y)
    X_tr_n, X_te_n, _ = prep.normalizar(X_tr, X_te)

    modelo = tr.treinar_regressao(X_tr_n, y_tr)
    av.avaliar_regressao(modelo, X_te_n, y_te)


def parte_C_agrupamento():
    print("\n" + "=" * 60)
    print(" PARTE C - AGRUPAMENTO: segmentar clientes (KMeans)")
    print("=" * 60)
    df = prep.carregar_csv("clientes.csv")
    X = df.drop(columns=["id_cliente"])      # nao usamos o id para agrupar
    X_norm, _, _ = prep.normalizar(X, X)     # normaliza para o KMeans
    modelo, grupos = tr.treinar_agrupamento(X_norm, n_grupos=3)
    av.plotar_agrupamento(
        X.values, grupos, col_x=0, col_y=1,
        nomes=("idade", "gasto_mensal")
    )
    # mostra o perfil medio de cada grupo descoberto
    df["grupo"] = grupos
    print("\n  Perfil medio de cada grupo:")
    print(df.groupby("grupo")[["idade", "gasto_mensal", "visitas_semana"]]
            .mean().round(1).to_string())


def parte_D_reforco():
    print("\n" + "=" * 60)
    print(" PARTE D - REFORCO: agente aprende um labirinto")
    print("=" * 60)
    Q, politica = tr.treinar_reforco_labirinto(episodios=300)
    print("  Melhor acao aprendida em cada posicao do corredor:")
    for i, a in enumerate(politica):
        print(f"     posicao {i} -> {a}")
    print("  (o agente aprendeu a sempre ir para a DIREITA ate o objetivo)")


if __name__ == "__main__":
    print("########################################################")
    print("#   AULA 02 - APRENDIZADO DE MAQUINA - PROJETO COMPLETO #")
    print("########################################################")
    parte_A_classificacao()
    parte_B_regressao()
    parte_C_agrupamento()
    parte_D_reforco()
    print("\n[FIM] Projeto executado com sucesso!")
    print("Veja os graficos gerados na pasta 'graficos/'.")
