# -*- coding: utf-8 -*-
"""
======================================================================
 avaliacao.py  -  AULA 02 (Aprendizado de Maquina)
----------------------------------------------------------------------
 Treinar um modelo nao basta: precisamos saber se ele e' BOM.
 Este modulo calcula as METRICAS e gera GRAFICOS de avaliacao.

   - Classificacao: Accuracy, Precision, Recall, F1, Matriz de Confusao
   - Regressao:     MAE, RMSE, R2
======================================================================
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")              # permite salvar graficos sem tela
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, mean_absolute_error, mean_squared_error, r2_score,
)

PASTA_GRAFICOS = os.path.join(os.path.dirname(__file__), "..", "graficos")
os.makedirs(PASTA_GRAFICOS, exist_ok=True)

VERMELHO = "#F00808"
SALMAO   = "#F36058"
AZUL     = "#2563EB"


# ---------------------------------------------------------------------
# CLASSIFICACAO
# ---------------------------------------------------------------------
def avaliar_classificacao(modelo, X_te, y_te):
    """Calcula as 4 metricas principais e mostra o que cada uma significa."""
    y_pred = modelo.predict(X_te)

    acc  = accuracy_score(y_te, y_pred)
    prec = precision_score(y_te, y_pred, zero_division=0)
    rec  = recall_score(y_te, y_pred, zero_division=0)
    f1   = f1_score(y_te, y_pred, zero_division=0)

    print("\n--- METRICAS DE CLASSIFICACAO ---")
    print(f"  Accuracy  : {acc:.2%}  (acertos no total)")
    print(f"  Precision : {prec:.2%}  (dos que previu 'sim', quantos eram 'sim')")
    print(f"  Recall    : {rec:.2%}  (dos 'sim' reais, quantos achou)")
    print(f"  F1-Score  : {f1:.2%}  (equilibrio entre precision e recall)")

    _plotar_matriz_confusao(y_te, y_pred)
    return {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1}


def _plotar_matriz_confusao(y_te, y_pred):
    """Desenha a Matriz de Confusao: compara o real com o previsto."""
    cm = confusion_matrix(y_te, y_pred)
    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(cm, cmap="Reds")
    rotulos = ["Negado (0)", "Aprovado (1)"]
    ax.set_xticks([0, 1]); ax.set_xticklabels(rotulos)
    ax.set_yticks([0, 1]); ax.set_yticklabels(rotulos)
    ax.set_xlabel("Previsto pelo modelo")
    ax.set_ylabel("Valor real")
    ax.set_title("Matriz de Confusao", color=VERMELHO, fontweight="bold")
    # escreve o numero em cada celula
    for i in range(2):
        for j in range(2):
            ax.text(j, i, cm[i, j], ha="center", va="center",
                    fontsize=16, fontweight="bold",
                    color="white" if cm[i, j] > cm.max()/2 else "black")
    fig.tight_layout()
    destino = os.path.join(PASTA_GRAFICOS, "matriz_confusao.png")
    fig.savefig(destino, dpi=130); plt.close(fig)
    print(f"  [grafico] salvo em graficos/matriz_confusao.png")


# ---------------------------------------------------------------------
# REGRESSAO
# ---------------------------------------------------------------------
def avaliar_regressao(modelo, X_te, y_te):
    """Calcula as metricas de regressao (erro em numeros)."""
    y_pred = modelo.predict(X_te)
    mae  = mean_absolute_error(y_te, y_pred)
    rmse = np.sqrt(mean_squared_error(y_te, y_pred))
    r2   = r2_score(y_te, y_pred)

    print("\n--- METRICAS DE REGRESSAO ---")
    print(f"  MAE  : {mae:.1f} mil R$  (erro medio em reais)")
    print(f"  RMSE : {rmse:.1f} mil R$  (penaliza erros grandes)")
    print(f"  R2   : {r2:.2%}  (o quanto o modelo explica os dados)")

    _plotar_real_vs_previsto(y_te, y_pred)
    return {"mae": mae, "rmse": rmse, "r2": r2}


def _plotar_real_vs_previsto(y_te, y_pred):
    """Grafico: quanto mais perto da linha tracejada, melhor a previsao."""
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.scatter(y_te, y_pred, color=SALMAO, edgecolors="white", s=60)
    lo = min(min(y_te), min(y_pred)); hi = max(max(y_te), max(y_pred))
    ax.plot([lo, hi], [lo, hi], "--", color=VERMELHO, label="previsao perfeita")
    ax.set_xlabel("Preco real (mil R$)")
    ax.set_ylabel("Preco previsto (mil R$)")
    ax.set_title("Real vs. Previsto", color=VERMELHO, fontweight="bold")
    ax.legend()
    fig.tight_layout()
    destino = os.path.join(PASTA_GRAFICOS, "regressao_real_vs_previsto.png")
    fig.savefig(destino, dpi=130); plt.close(fig)
    print(f"  [grafico] salvo em graficos/regressao_real_vs_previsto.png")


# ---------------------------------------------------------------------
# AGRUPAMENTO (visualizacao dos clusters)
# ---------------------------------------------------------------------
def plotar_agrupamento(X, grupos, col_x=0, col_y=1, nomes=("eixo X", "eixo Y")):
    """Mostra os grupos descobertos pelo KMeans, cada cor = um grupo."""
    X = np.asarray(X)
    fig, ax = plt.subplots(figsize=(5.5, 4))
    cores = ["#F00808", "#2563EB", "#16A34A", "#D97706", "#7C3AED"]
    for g in np.unique(grupos):
        sel = grupos == g
        ax.scatter(X[sel, col_x], X[sel, col_y], s=60, alpha=0.8,
                   color=cores[g % len(cores)], label=f"Grupo {g}",
                   edgecolors="white")
    ax.set_xlabel(nomes[0]); ax.set_ylabel(nomes[1])
    ax.set_title("Segmentacao de Clientes (KMeans)", color=VERMELHO, fontweight="bold")
    ax.legend()
    fig.tight_layout()
    destino = os.path.join(PASTA_GRAFICOS, "clusters_clientes.png")
    fig.savefig(destino, dpi=130); plt.close(fig)
    print(f"  [grafico] salvo em graficos/clusters_clientes.png")


if __name__ == "__main__":
    print("Este modulo e' usado pelo main.py. Rode 'python main.py'.")
