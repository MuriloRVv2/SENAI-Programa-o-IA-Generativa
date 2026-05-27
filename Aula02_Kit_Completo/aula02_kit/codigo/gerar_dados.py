# -*- coding: utf-8 -*-
"""
Gerador das bases de dados da Aula 02.
Cria: clientes.csv, vendas.csv, classificacao.csv
Dados realistas, pequenos e faceis de entender.
"""
import numpy as np
import pandas as pd
import os

np.random.seed(42)
DEST = os.path.join(os.path.dirname(__file__), "..", "dados")
os.makedirs(DEST, exist_ok=True)

# ----------------------------------------------------------------------
# 1) clientes.csv  -> usado em APRENDIZADO NAO SUPERVISIONADO (KMeans)
#    Segmentacao de clientes por comportamento de compra.
# ----------------------------------------------------------------------
n = 60
# 3 perfis "naturais" para o KMeans descobrir sozinho
perfis = (
    [( 25, 1500,  4)] * 20 +   # jovens, gasto baixo, muitas visitas
    [( 45, 6000,  2)] * 20 +   # adultos, gasto alto, poucas visitas
    [( 60, 3000,  1)] * 20     # idosos, gasto medio, visita rara
)
clientes = pd.DataFrame(perfis, columns=["idade", "gasto_mensal", "visitas_semana"])
# adiciona ruido realista
clientes["idade"]          += np.random.randint(-5, 6, n)
clientes["gasto_mensal"]   += np.random.randint(-500, 501, n)
clientes["visitas_semana"]  = (clientes["visitas_semana"] + np.random.randint(0, 2, n)).clip(0)
clientes.insert(0, "id_cliente", range(1, n + 1))
clientes.to_csv(f"{DEST}/clientes.csv", index=False)
print(f"clientes.csv      -> {clientes.shape[0]} linhas")

# ----------------------------------------------------------------------
# 2) vendas.csv  -> usado em REGRESSAO (prever preco do imovel)
#    Relacao clara entre area/quartos/idade e preco.
# ----------------------------------------------------------------------
m = 80
vendas = pd.DataFrame({
    "area_m2":     np.random.randint(40, 200, m),
    "quartos":     np.random.randint(1, 5, m),
    "idade_imovel":np.random.randint(0, 30, m),
    "garagem":     np.random.choice([0, 1], m, p=[0.4, 0.6]),
})
# preco (em mil R$) com relacao realista + ruido
vendas["preco_mil"] = (
    vendas["area_m2"] * 3.2
    + vendas["quartos"] * 25
    - vendas["idade_imovel"] * 1.5
    + vendas["garagem"] * 30
    + np.random.normal(0, 15, m)
).round(1).clip(lower=80)
vendas.to_csv(f"{DEST}/vendas.csv", index=False)
print(f"vendas.csv        -> {vendas.shape[0]} linhas")

# ----------------------------------------------------------------------
# 3) classificacao.csv -> usado em CLASSIFICACAO (aprovar credito)
#    Inclui 1 coluna categorica (faz_curso) e alguns valores faltantes.
# ----------------------------------------------------------------------
k = 100
clf = pd.DataFrame({
    "idade":        np.random.randint(18, 70, k),
    "renda_mil":    np.round(np.random.uniform(1.0, 15.0, k), 1),
    "dividas_mil":  np.round(np.random.uniform(0.0, 20.0, k), 1),
    "anos_emprego": np.random.randint(0, 25, k),
    "tem_imovel":   np.random.choice(["sim", "nao"], k, p=[0.45, 0.55]),
})
# regra de aprovacao: boa renda, poucas dividas, estabilidade
score = (
    clf["renda_mil"] * 0.4
    - clf["dividas_mil"] * 0.5
    + clf["anos_emprego"] * 0.3
    + (clf["tem_imovel"] == "sim").astype(int) * 2.0
)
clf["aprovado"] = (score > score.median()).astype(int)  # 1 = aprovado, 0 = negado
# introduz ~5% de valores faltantes em 'renda_mil' (para praticar limpeza)
faltam = np.random.choice(clf.index, 5, replace=False)
clf.loc[faltam, "renda_mil"] = np.nan
clf.to_csv(f"{DEST}/classificacao.csv", index=False)
print(f"classificacao.csv -> {clf.shape[0]} linhas | nulos: {clf.isnull().sum().sum()} | aprovados: {clf['aprovado'].sum()}")

print("\nTodas as bases foram geradas na pasta 'dados/'.")
