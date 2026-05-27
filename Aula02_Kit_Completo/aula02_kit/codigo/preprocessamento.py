# -*- coding: utf-8 -*-
"""
======================================================================
 preprocessamento.py  -  AULA 02 (Aprendizado de Maquina)
----------------------------------------------------------------------
 Este modulo cuida da PREPARACAO DOS DADOS antes de treinar um modelo.
 Pre-processar e' transformar dados "crus" em dados "limpos e numericos".

 Etapas que fazemos aqui:
   1. Carregar o CSV (Pandas)
   2. Tratar valores faltantes (limpeza)
   3. Converter texto em numero (encoding)
   4. Separar X (entradas) e y (resposta)
   5. Dividir em treino e teste
   6. Normalizar (deixar tudo na mesma escala)
======================================================================
"""
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Caminho base dos dados (pasta ../dados em relacao a este arquivo)
PASTA_DADOS = os.path.join(os.path.dirname(__file__), "..", "dados")


def carregar_csv(nome_arquivo):
    """Le um arquivo CSV da pasta 'dados' e devolve um DataFrame do Pandas.
    DataFrame = uma tabela, como uma planilha do Excel."""
    caminho = os.path.join(PASTA_DADOS, nome_arquivo)
    df = pd.read_csv(caminho)
    print(f"[OK] '{nome_arquivo}' carregado: {df.shape[0]} linhas e {df.shape[1]} colunas")
    return df


def tratar_faltantes(df):
    """Preenche valores faltantes (NaN) das colunas numericas com a MEDIA.
    Por que? Porque a maioria dos modelos nao aceita celulas vazias."""
    df = df.copy()
    colunas_numericas = df.select_dtypes(include="number").columns
    for col in colunas_numericas:
        if df[col].isnull().any():
            media = df[col].mean()
            df[col] = df[col].fillna(media)
            print(f"   - coluna '{col}': faltantes preenchidos com a media ({media:.2f})")
    return df


def codificar_categoricas(df):
    """Converte colunas de TEXTO em NUMERO (encoding).
    Ex.: a coluna 'tem_imovel' com 'sim'/'nao' vira 1/0.
    Modelos so entendem numeros, nunca texto."""
    df = df.copy()
    colunas_texto = df.select_dtypes(include="object").columns
    for col in colunas_texto:
        # get_dummies cria colunas 0/1; drop_first evita coluna redundante
        dummies = pd.get_dummies(df[col], prefix=col, drop_first=True).astype(int)
        df = pd.concat([df.drop(columns=[col]), dummies], axis=1)
        print(f"   - coluna '{col}': convertida em numero (encoding)")
    return df


def separar_X_y(df, coluna_alvo):
    """Separa a tabela em:
       X = tudo o que o modelo USA para prever (as 'pistas')
       y = o que o modelo DEVE prever (a 'resposta certa')"""
    X = df.drop(columns=[coluna_alvo])
    y = df[coluna_alvo]
    print(f"   - X (entradas): {X.shape[1]} colunas | y (alvo): '{coluna_alvo}'")
    return X, y


def dividir_treino_teste(X, y, teste=0.2):
    """Divide os dados em TREINO (estudar) e TESTE (prova).
    Treinamos com 80% e avaliamos com 20% que o modelo nunca viu."""
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=teste, random_state=42
    )
    print(f"   - treino: {len(X_tr)} linhas | teste: {len(X_te)} linhas")
    return X_tr, X_te, y_tr, y_te


def normalizar(X_tr, X_te):
    """Coloca todas as colunas na MESMA escala (media 0, desvio 1).
    Importante: aprendemos a escala SO no treino e aplicamos no teste.
    Isso evita 'vazamento' de informacao do teste para o treino."""
    scaler = StandardScaler()
    X_tr_norm = scaler.fit_transform(X_tr)   # aprende + aplica no treino
    X_te_norm = scaler.transform(X_te)       # apenas aplica no teste
    print("   - dados normalizados (mesma escala)")
    return X_tr_norm, X_te_norm, scaler


# Teste rapido se rodar este arquivo sozinho
if __name__ == "__main__":
    print(">> Testando o modulo de pre-processamento com classificacao.csv\n")
    df = carregar_csv("classificacao.csv")
    df = tratar_faltantes(df)
    df = codificar_categoricas(df)
    X, y = separar_X_y(df, "aprovado")
    X_tr, X_te, y_tr, y_te = dividir_treino_teste(X, y)
    X_tr_n, X_te_n, _ = normalizar(X_tr, X_te)
    print("\n[OK] Pre-processamento concluido com sucesso!")
