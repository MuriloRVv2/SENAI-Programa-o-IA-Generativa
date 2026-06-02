# =============================================================================
#  MODULO 3.1 — ARQUITETURA DE REDES NEURAIS
#  Dataset: dados_falsos_Imobiliario.csv
#  Objetivo: Prever o PRECO DE UM IMOVEL
# =============================================================================
#
#  O QUE ESTE SCRIPT FAZ (em palavras simples):
#  Imagine uma fabrica de avaliacoes de imoveis. Voce entra com as informacoes
#  de um imovel (area, quartos, tem piscina?...) e a fabrica te diz o preco.
#  Cada "estacao de trabalho" dentro da fabrica e uma CAMADA da rede neural.
#  Quanto mais estacos, mais refinada a avaliacao.
#
#  COMO RODAR NO GOOGLE COLAB:
#  1. Abra colab.research.google.com
#  2. Cole este codigo numa celula
#  3. Execute com Ctrl+Enter
#  4. Quando pedir o arquivo CSV, faca o upload do seu computador
#
#  PACOTES NECESSARIOS (rode esta linha primeiro no Colab):
#  !pip install tensorflow pandas scikit-learn matplotlib tqdm
# =============================================================================

# ── IMPORTACOES ───────────────────────────────────────────────────────────────
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tqdm import tqdm

# ── SEMENTE ALEATORIA ─────────────────────────────────────────────────────────
# Fixamos o numero 42 para garantir resultados identicos a cada execucao.
# O numero 42 e uma referencia classica ao livro "O Guia do Mochileiro das Galaxias".
tf.random.set_seed(42)
np.random.seed(42)
random.seed(42)

print("=" * 65)
print("  MODULO 3.1 — ARQUITETURA DE REDES NEURAIS ARTIFICIAIS")
print("=" * 65)
print(f"  Versao do TensorFlow: {tf.__version__}")
print("  Dataset: Imoveis | Objetivo: Prever o valor em R$")
print("=" * 65)

# =============================================================================
#  PASSO 1: CARREGANDO OS DADOS
# =============================================================================
# O arquivo CSV e como uma planilha do Excel com informacoes de imoveis.
# Cada linha e um imovel. Cada coluna e uma caracteristica dele.

try:
    from google.colab import files
    print("\n  Selecione o arquivo CSV no seu computador:")
    uploaded = files.upload()
    CAMINHO_CSV = list(uploaded.keys())[0]
    print(f"  Arquivo '{CAMINHO_CSV}' carregado!")
except ImportError:
    CAMINHO_CSV = "dados_falsos_Imobiliario.csv"
    print(f"\n  Lendo arquivo local: {CAMINHO_CSV}")

df = pd.read_csv(CAMINHO_CSV)
print(f"\n  Dados carregados!")
print(f"  Total de imoveis : {len(df):,}")
print(f"  Total de colunas : {len(df.columns)}")
print(f"\n  Primeiros 3 imoveis da tabela:")
print(df.head(3).to_string())

# =============================================================================
#  PASSO 2: PREPARANDO OS DADOS
# =============================================================================
# A rede neural so entende NUMEROS.
# Precisamos converter texto ("Sim"/"Nao") para numeros (1/0).
#
# CORRECAO APLICADA: o CSV usa "Nao" com acento (Não).
# O map correto precisa usar 'Não' (com til), nao 'Nao'.

print("\n\n  Preparando os dados...")

# Removemos colunas que nao serao usadas pelo modelo
# CPF e Endereco sao dados pessoais — nao faz sentido usa-los para prever preco
df.drop(columns=['CPF', 'Endereço do Imóvel'], inplace=True)

# CORRECAO 1: Convertendo "Sim" e "Não" para 1 e 0
# ATENCAO: o CSV usa "Não" (com til). Usar "Nao" causaria NaN em 50% das linhas!
colunas_binarias = ['Tem Piscina?', 'Tem Garagem?', 'Tem Elevador?', 'Condomínio Fechado?']
for col in colunas_binarias:
    df[col] = df[col].map({'Sim': 1, 'Não': 0})   # <-- 'Não' com til (correto!)
    print(f"    '{col}': Sim=1, Não=0")

# CORRECAO 2: Renomeando as colunas para nomes sem acento (compativel com FEATURES abaixo)
# O CSV usa acentos: "Área do Imóvel (m²)". Renomeamos para facilitar o manuseio.
df.rename(columns={
    'Área do Imóvel (m²)':   'Area do Imovel (m2)',
    'Valor do Imóvel':        'Valor do Imovel',
    'Número de Quartos':      'Numero de Quartos',
    'Número de Banheiros':    'Numero de Banheiros',
    'Valor do Condomínio':    'Valor do Condominio',
    'Ano de Construção':      'Ano de Construcao',
    'Tipo de Imóvel':         'Tipo de Imovel',
    'Condomínio Fechado?':    'Condominio Fechado?',
}, inplace=True)

# Convertendo Tipo de Imovel e Tipo de Oferta com One-Hot Encoding
# Ex: "Apartamento" vira coluna propria com 1 (e apartamento) ou 0 (nao e)
df = pd.get_dummies(df, columns=['Tipo de Imovel', 'Tipo de Oferta'], drop_first=True)

# ── DEFININDO FEATURES E TARGET ───────────────────────────────────────────────
# FEATURES (X) = ingredientes que ENTRAM na rede neural
# TARGET   (y) = o resultado que ela deve PREVER (o preco)

FEATURES = [
    'Area do Imovel (m2)',
    'Numero de Quartos',
    'Numero de Banheiros',
    'Valor do Condominio',
    'Ano de Construcao',
    'Tem Piscina?',
    'Tem Garagem?',
    'Tem Elevador?',
    'Condominio Fechado?',
]
TARGET = 'Valor do Imovel'

X = df[FEATURES].values
y = df[TARGET].values

print(f"\n  Features usadas ({len(FEATURES)} colunas):")
for i, f in enumerate(FEATURES, 1):
    print(f"    {i:2d}. {f}")
print(f"\n  Target: {TARGET}")
print(f"  Preco minimo: R$ {y.min():,.0f}")
print(f"  Preco maximo: R$ {y.max():,.0f}")
print(f"  Preco medio : R$ {y.mean():,.0f}")

# =============================================================================
#  PASSO 3: DIVIDINDO EM TREINO E TESTE
# =============================================================================
# ANALOGIA DA PROVA ESCOLAR:
# TREINO (80%) = questoes que o aluno estuda
# TESTE  (20%) = prova final com questoes novas que ele nunca viu
#
# Se a IA vai bem no TESTE, ela realmente aprendeu.
# Se foi mal, ela so memorizou (overfitting).

X_treino, X_teste, y_treino, y_teste = train_test_split(
    X, y, test_size=0.20, random_state=42
)

print(f"\n  Divisao dos dados:")
print(f"  Treino: {X_treino.shape[0]:,} imoveis ({X_treino.shape[0]/len(X)*100:.0f}%)")
print(f"  Teste : {X_teste.shape[0]:,} imoveis ({X_teste.shape[0]/len(X)*100:.0f}%)")

# =============================================================================
#  PASSO 4: NORMALIZACAO
# =============================================================================
# PROBLEMA: as features tem escalas diferentes.
#   - Area: 50 a 500 m2
#   - Ano: 1980 a 2023
#   - Condominio: R$ 200 a R$ 2.000
#
# Solucao: MinMaxScaler transforma tudo para o intervalo [0, 1].
# O MENOR valor vira 0, o MAIOR vira 1, os do meio ficam proporcionais.
#
# REGRA DE OURO: o scaler aprende SOMENTE com dados de treino!
# Usar o teste para aprender seria dar o gabarito da prova para o aluno.

scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()

X_treino_n = scaler_X.fit_transform(X_treino)
y_treino_n = scaler_y.fit_transform(y_treino.reshape(-1, 1)).flatten()

X_teste_n  = scaler_X.transform(X_teste)
y_teste_n  = scaler_y.transform(y_teste.reshape(-1, 1)).flatten()

print(f"\n  Normalizacao:")
print(f"  Area original  : {X_treino[0][0]:.1f} m2  →  Area normalizada: {X_treino_n[0][0]:.4f}")
print(f"  Preco original : R$ {y_treino[0]:,.0f}  →  Preco normalizado: {y_treino_n[0]:.4f}")

# =============================================================================
#  PASSO 5: CONSTRUINDO A ARQUITETURA DA REDE NEURAL
# =============================================================================
# ANALOGIA DA FABRICA DE AVALIACOES:
#
# ENTRADA  → 9 caracteristicas do imovel chegam na fabrica
#    |
#    v  [64 trabalhadores analisam e detectam padroes basicos]
# CAMADA 1 → "imoveis grandes tendem a custar mais"
#    |
#    v  [32 trabalhadores combinam os padroes]
# CAMADA 2 → "imovel grande + piscina = alto padrao"
#    |
#    v  [16 trabalhadores fazem o refinamento final]
# CAMADA 3 → ajuste fino
#    |
#    v  [1 avaliador final calcula o preco]
# SAIDA    → "Este imovel vale R$ 850.000"
#
# RELU = o "porteiro" que bloqueia sinais negativos (neuronios inativos)
# DROPOUT = treina sem alguns neuronios por vez (evita "decoreba")

modelo = keras.Sequential(name="Fabrica_de_Avaliacao_Imobiliaria")

modelo.add(layers.Input(shape=(len(FEATURES),), name="Entrada_Dados_do_Imovel"))
modelo.add(layers.Dense(64, activation='relu',   name="Estacao_1_Padroes_Basicos"))
modelo.add(layers.Dropout(0.2,                   name="Dropout_1_Anti_Decoreba"))
modelo.add(layers.Dense(32, activation='relu',   name="Estacao_2_Padroes_Complexos"))
modelo.add(layers.Dropout(0.2,                   name="Dropout_2_Anti_Decoreba"))
modelo.add(layers.Dense(16, activation='relu',   name="Estacao_3_Refinamento_Final"))
modelo.add(layers.Dense(1,  activation='linear', name="Saida_Preco_Previsto"))

print("\n" + "=" * 65)
print("  ESTRUTURA DA NOSSA FABRICA (Rede Neural):")
print("=" * 65)
modelo.summary()

total_params = modelo.count_params()
print(f"\n  Total de parametros aprendidos: {total_params:,}")
print(f"  E como uma mesa de som com {total_params:,} controles deslizantes!")

# =============================================================================
#  PASSO 6: COMPILACAO
# =============================================================================
# OTIMIZADOR Adam: o "tecnico" que ajusta os pesos apos cada rodada.
# MAE (Erro Medio Absoluto): em media, erramos R$ X no preco previsto.
# Ex: MAE de R$ 80.000 = a IA erra em media R$ 80.000 para mais ou para menos.

modelo.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='mae',
    metrics=['mse']
)

print("\n  Fabrica configurada!")
print("  Otimizador : Adam")
print("  Metrica    : MAE (Erro Medio Absoluto em R$)")

# =============================================================================
#  PASSO 7: BARRA DE PROGRESSO
# =============================================================================

class BarraDeProgresso(keras.callbacks.Callback):
    """Exibe progresso do treino com barra visual no terminal."""

    def __init__(self, total_epocas):
        super().__init__()
        self.total_epocas = total_epocas
        self.barra = None

    def on_train_begin(self, logs=None):
        self.barra = tqdm(
            total=self.total_epocas,
            desc="  Aprendendo",
            unit=" epoca",
            colour="green",
            bar_format="{l_bar}{bar:40}{r_bar}",
            ncols=90
        )

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        self.barra.set_postfix({
            "treino": f"{logs.get('loss', 0):.4f}",
            "validacao": f"{logs.get('val_loss', 0):.4f}",
        })
        self.barra.update(1)

    def on_train_end(self, logs=None):
        self.barra.close()
        print("\n  Aprendizado concluido!")

# =============================================================================
#  PASSO 8: TREINAMENTO
# =============================================================================
# EPOCAS: quantas vezes a IA vai "reler" todos os dados.
# BATCH SIZE: quantos imoveis analisa antes de fazer uma correcao.
#
# EarlyStopping: para automaticamente se o modelo parar de melhorar.
# patience=12 significa que aguarda 12 epocas sem melhora antes de parar.

EPOCAS     = 60
BATCH_SIZE = 256

print(f"\n{'─' * 65}")
print(f"  Iniciando treino:")
print(f"  - Epocas    : {EPOCAS}")
print(f"  - Batch size: {BATCH_SIZE} imoveis por correcao")
print(f"  - Treino    : {X_treino_n.shape[0]:,} imoveis")
print(f"{'─' * 65}\n")

historico = modelo.fit(
    X_treino_n, y_treino_n,
    validation_split=0.15,
    epochs=EPOCAS,
    batch_size=BATCH_SIZE,
    callbacks=[
        BarraDeProgresso(EPOCAS),
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=12,
            restore_best_weights=True,
            verbose=0
        )
    ],
    verbose=0
)

epocas_reais = len(historico.history['loss'])
print(f"\n  EarlyStopping parou na epoca {epocas_reais} (economizou {EPOCAS - epocas_reais} epocas)!")

# =============================================================================
#  FUNCAO DE PREVISAO
# =============================================================================

def prever_preco(imovel_dict):
    """
    Recebe as caracteristicas de um imovel e retorna o preco previsto.

    Processo interno:
    1. Organiza as features na ordem correta
    2. Normaliza para o intervalo [0, 1] (usando o scaler do treino)
    3. Passa pela rede neural
    4. Desnormaliza de volta para R$
    """
    X_novo   = np.array([[imovel_dict[f] for f in FEATURES]], dtype=np.float32)
    X_novo_n = scaler_X.transform(X_novo)
    pred_n   = modelo.predict(X_novo_n, verbose=0)[0][0]
    preco    = scaler_y.inverse_transform([[pred_n]])[0][0]
    return preco


def gerar_imovel_aleatorio(perfil='aleatorio', seed=None):
    """Cria um imovel ficticio para testes."""
    if seed is not None:
        random.seed(seed)
    if perfil == 'luxo':
        return {
            'Area do Imovel (m2)':  round(random.uniform(350, 500), 1),
            'Numero de Quartos':    random.randint(4, 5),
            'Numero de Banheiros':  random.randint(4, 7),
            'Valor do Condominio':  round(random.uniform(1500, 2000), 2),
            'Ano de Construcao':    random.randint(2015, 2023),
            'Tem Piscina?':         1,
            'Tem Garagem?':         1,
            'Tem Elevador?':        1,
            'Condominio Fechado?':  1,
        }
    elif perfil == 'simples':
        return {
            'Area do Imovel (m2)':  round(random.uniform(50, 100), 1),
            'Numero de Quartos':    random.randint(1, 2),
            'Numero de Banheiros':  random.randint(1, 2),
            'Valor do Condominio':  round(random.uniform(200, 400), 2),
            'Ano de Construcao':    random.randint(1980, 1999),
            'Tem Piscina?':         0,
            'Tem Garagem?':         0,
            'Tem Elevador?':        0,
            'Condominio Fechado?':  0,
        }
    elif perfil == 'medio':
        return {
            'Area do Imovel (m2)':  round(random.uniform(150, 280), 1),
            'Numero de Quartos':    random.randint(2, 3),
            'Numero de Banheiros':  random.randint(2, 3),
            'Valor do Condominio':  round(random.uniform(600, 1200), 2),
            'Ano de Construcao':    random.randint(2000, 2015),
            'Tem Piscina?':         random.randint(0, 1),
            'Tem Garagem?':         1,
            'Tem Elevador?':        random.randint(0, 1),
            'Condominio Fechado?':  random.randint(0, 1),
        }
    else:
        return {
            'Area do Imovel (m2)':  round(random.uniform(50, 500), 1),
            'Numero de Quartos':    random.randint(1, 5),
            'Numero de Banheiros':  random.randint(1, 7),
            'Valor do Condominio':  round(random.uniform(200, 2000), 2),
            'Ano de Construcao':    random.randint(1980, 2023),
            'Tem Piscina?':         random.randint(0, 1),
            'Tem Garagem?':         random.randint(0, 1),
            'Tem Elevador?':        random.randint(0, 1),
            'Condominio Fechado?':  random.randint(0, 1),
        }

# =============================================================================
#  PASSO 9: TESTES COM IMOVEIS FICTICIOS
# =============================================================================

print(f"\n{'=' * 65}")
print("  TESTE: A IA aprendeu direito?")
print("  Vamos avaliar 5 imoveis ficticios.")
print(f"{'=' * 65}\n")

cenarios = [
    ('Imovel de Luxo',     'luxo',      1),
    ('Casa Simples',       'simples',   2),
    ('Apartamento Medio',  'medio',     3),
    ('Imovel Aleatorio A', 'aleatorio', 42),
    ('Imovel Aleatorio B', 'aleatorio', 99),
]

precos_previstos = []
for nome, perfil, seed in cenarios:
    imovel = gerar_imovel_aleatorio(perfil=perfil, seed=seed)
    preco  = prever_preco(imovel)
    precos_previstos.append((nome, preco, imovel))

    icone = {"Imovel de Luxo": "💎", "Casa Simples": "🏠",
             "Apartamento Medio": "🏢"}.get(nome, "🏗")

    print(f"  {icone} {nome}")
    print(f"     Area: {imovel['Area do Imovel (m2)']:>6.1f}m²  |  "
          f"Quartos: {imovel['Numero de Quartos']}  |  Ano: {imovel['Ano de Construcao']}")
    piscina = 'Sim' if imovel['Tem Piscina?'] else 'Nao'
    garagem = 'Sim' if imovel['Tem Garagem?'] else 'Nao'
    print(f"     Piscina: {piscina}  |  Garagem: {garagem}  |  "
          f"Cond. Fechado: {'Sim' if imovel['Condominio Fechado?'] else 'Nao'}")
    print(f"     >> PRECO PREVISTO: R$ {preco:>13,.2f}")
    print()

luxo_preco    = precos_previstos[0][1]
simples_preco = precos_previstos[1][1]
print(f"  Verificacao de sanidade:")
print(f"  Luxo   : R$ {luxo_preco:,.0f}")
print(f"  Simples: R$ {simples_preco:,.0f}")
if luxo_preco > simples_preco:
    print(f"  Resultado: OK! Luxo > Simples (diferenca: R$ {luxo_preco - simples_preco:,.0f})")
else:
    print(f"  ATENCAO: algo parece errado — o simples ficou mais caro!")

# =============================================================================
#  PASSO 10: EXPERIMENTO — IMPACTO DE CADA CARACTERISTICA
# =============================================================================

print(f"\n{'─' * 65}")
print("  EXPERIMENTO: quanto cada caracteristica influencia o preco?")
print(f"{'─' * 65}")

imovel_base = {
    'Area do Imovel (m2)': 150, 'Numero de Quartos': 2, 'Numero de Banheiros': 2,
    'Valor do Condominio': 800, 'Ano de Construcao': 2005,
    'Tem Piscina?': 0, 'Tem Garagem?': 0, 'Tem Elevador?': 0, 'Condominio Fechado?': 0
}
preco_base = prever_preco(imovel_base)
print(f"\n  Imovel BASE (150m², 2 quartos, sem extras): R$ {preco_base:,.0f}\n")

experimentos = [
    ("+ Piscina",          {'Tem Piscina?': 1}),
    ("+ Garagem",          {'Tem Garagem?': 1}),
    ("+ Elevador",         {'Tem Elevador?': 1}),
    ("+ Cond. Fechado",    {'Condominio Fechado?': 1}),
    ("+ 50m2 de area",     {'Area do Imovel (m2)': 200}),
    ("+ 1 quarto a mais",  {'Numero de Quartos': 3}),
    ("Construcao recente", {'Ano de Construcao': 2022}),
    ("TUDO junto",         {'Tem Piscina?': 1, 'Tem Garagem?': 1, 'Tem Elevador?': 1,
                            'Condominio Fechado?': 1, 'Area do Imovel (m2)': 200,
                            'Numero de Quartos': 3, 'Ano de Construcao': 2022}),
]

impactos = []
for descricao, alteracao in experimentos:
    mod = imovel_base.copy()
    mod.update(alteracao)
    preco_novo  = prever_preco(mod)
    diferenca   = preco_novo - preco_base
    percentual  = (diferenca / preco_base) * 100
    seta        = "▲" if diferenca > 0 else "▼"
    impactos.append({'desc': descricao, 'dif': diferenca, 'pct': percentual})
    print(f"  {seta} {descricao:<22} → R$ {preco_novo:>12,.0f}  "
          f"({seta} R$ {abs(diferenca):>9,.0f} / {seta}{abs(percentual):.1f}%)")

# =============================================================================
#  PASSO 11: GRAFICOS DE EVOLUCAO DO TREINO
# =============================================================================
# Aqui visualizamos COMO o modelo aprendeu ao longo do tempo.
#
# Grafico 1 — Curva de aprendizado (MAE): mostra como o erro foi caindo.
#   Uma curva saudavel: o erro desce rapidamente no inicio e estabiliza.
#   Se treino e validacao estiverem muito separados, ha overfitting.
#
# Grafico 2 — Curva MSE: penaliza erros grandes mais forte que o MAE.
#   Util para identificar se o modelo teve "tropecos" em alguns casos.
#
# Grafico 3 — Taxa de melhora por epoca: mostra o "ritmo" do aprendizado.
#   O gradiente do MAE — quando chega a zero, o modelo parou de aprender.
#
# Grafico 4 — Diferenca treino vs validacao: mede o risco de overfitting.
#   Ideal: linha proxima de zero. Se subir muito, o modelo "decorou".
#
# Grafico 5 — Precos previstos por cenario: sanity check visual.
#
# Grafico 6 — Impacto de cada caracteristica: feature importance visual.

epocas_range = range(1, epocas_reais + 1)
loss_treino  = historico.history['loss']
loss_val     = historico.history['val_loss']
mse_treino   = historico.history.get('mse', [])
mse_val      = historico.history.get('val_mse', [])

fig = plt.figure(figsize=(20, 14))
fig.suptitle("Modulo 3.1 — Evolucao do Treino da Rede Neural",
             fontsize=15, fontweight='bold', y=0.98)

gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

# ── GRAFICO 1: Curva MAE (erro principal) ────────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(epocas_range, loss_treino, color='#2196F3', lw=2.5, label='Treino',    zorder=3)
ax1.plot(epocas_range, loss_val,    color='#FF5722', lw=2.5, label='Validacao', zorder=3, ls='--')
ax1.axvline(epocas_reais, color='gray', lw=1, ls=':', alpha=0.7)
ax1.text(epocas_reais - 1, max(loss_treino) * 0.95,
         f'Parou\n(ep. {epocas_reais})', fontsize=8, ha='right', color='gray')
ax1.fill_between(epocas_range, loss_treino, loss_val, alpha=0.08, color='purple')
ax1.set_title("Curva de Aprendizado (MAE)\nErro medio por epoca", fontsize=10, fontweight='bold')
ax1.set_xlabel("Epoca")
ax1.set_ylabel("MAE normalizado")
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)
ax1.set_xlim(1, epocas_reais)

# ── GRAFICO 2: Curva MSE ─────────────────────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
if mse_treino:
    ax2.plot(epocas_range, mse_treino, color='#9C27B0', lw=2.5, label='Treino')
    ax2.plot(epocas_range, mse_val,    color='#FF9800', lw=2.5, label='Validacao', ls='--')
    ax2.fill_between(epocas_range, mse_treino, mse_val, alpha=0.08, color='orange')
ax2.set_title("Erro Quadratico Medio (MSE)\nPenaliza erros grandes", fontsize=10, fontweight='bold')
ax2.set_xlabel("Epoca")
ax2.set_ylabel("MSE normalizado")
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3)
ax2.set_xlim(1, epocas_reais)

# ── GRAFICO 3: Taxa de melhora (gradiente do MAE) ────────────────────────────
ax3 = fig.add_subplot(gs[0, 2])
if len(loss_val) > 1:
    gradiente = np.diff(loss_val)
    cores_grad = ['#4CAF50' if g < 0 else '#F44336' for g in gradiente]
    ax3.bar(range(2, epocas_reais + 1), gradiente, color=cores_grad, alpha=0.8, width=0.8)
    ax3.axhline(0, color='black', lw=1)
    ax3.set_title("Taxa de Melhora por Epoca\nVerde=melhorou | Vermelho=piorou",
                  fontsize=10, fontweight='bold')
    ax3.set_xlabel("Epoca")
    ax3.set_ylabel("Variacao do MAE")
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.set_xlim(1, epocas_reais + 1)

# ── GRAFICO 4: Diferenca treino vs validacao (risco de overfitting) ───────────
ax4 = fig.add_subplot(gs[1, 0])
diff = [abs(t - v) for t, v in zip(loss_treino, loss_val)]
ax4.plot(epocas_range, diff, color='#795548', lw=2.5)
ax4.fill_between(epocas_range, diff, alpha=0.2, color='#795548')
ax4.axhline(np.mean(diff), color='red', lw=1, ls='--', label=f'Media: {np.mean(diff):.4f}')
ax4.set_title("Diferenca Treino x Validacao\nAlta = risco de overfitting",
              fontsize=10, fontweight='bold')
ax4.set_xlabel("Epoca")
ax4.set_ylabel("|MAE_treino - MAE_val|")
ax4.legend(fontsize=9)
ax4.grid(True, alpha=0.3)
ax4.set_xlim(1, epocas_reais)

# ── GRAFICO 5: Precos previstos por cenario ───────────────────────────────────
ax5 = fig.add_subplot(gs[1, 1])
nomes  = [p[0].replace(' ', '\n') for p in precos_previstos]
precos = [p[1] for p in precos_previstos]
cores5 = ['#4CAF50', '#F44336', '#2196F3', '#9C27B0', '#FF9800']
bars   = ax5.bar(range(len(nomes)), [p / 1e6 for p in precos],
                 color=cores5, edgecolor='white', width=0.6)
ax5.set_xticks(range(len(nomes)))
ax5.set_xticklabels(nomes, fontsize=8)
ax5.set_title("Precos Previstos\npor Tipo de Imovel", fontsize=10, fontweight='bold')
ax5.set_ylabel("Valor (R$ Milhoes)")
for bar, val in zip(bars, precos):
    ax5.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
             f'R${val/1e6:.2f}M', ha='center', va='bottom', fontsize=8, fontweight='bold')
ax5.grid(True, alpha=0.3, axis='y')

# ── GRAFICO 6: Impacto de cada caracteristica ─────────────────────────────────
ax6 = fig.add_subplot(gs[1, 2])
descs  = [i['desc'] for i in impactos]
diffs  = [i['dif']  for i in impactos]
cores6 = ['#4CAF50' if d > 0 else '#F44336' for d in diffs]
ax6.barh(descs, [d / 1e3 for d in diffs], color=cores6, edgecolor='white', height=0.7)
ax6.axvline(0, color='black', lw=1)
ax6.set_title("Impacto de Cada Caracteristica\nem relacao ao imovel base",
              fontsize=10, fontweight='bold')
ax6.set_xlabel("Variacao (R$ mil)")
ax6.grid(True, alpha=0.3, axis='x')

plt.savefig("3_1_evolucao_treino.png", dpi=150, bbox_inches='tight')
plt.show()
print("\n  Graficos salvos: '3_1_evolucao_treino.png'")

# =============================================================================
#  PASSO 12: PREVISAO INTERATIVA — O USUARIO DIGITA OS DADOS
# =============================================================================
# Agora vem a parte mais legal: voce, o usuario, informa as caracteristicas
# de um imovel REAL (ou imaginario) e a IA calcula o preco!
#
# ANALOGIA DA CALCULADORA:
# Antes, a IA aprendeu sozinha como calcular.
# Agora ela esta pronta — e so voce digitar os numeros.

def sim_nao_para_int(pergunta):
    """Faz uma pergunta Sim/Nao e retorna 1 ou 0."""
    while True:
        resp = input(pergunta).strip().lower()
        if resp in ('s', 'sim', '1'):
            return 1
        elif resp in ('n', 'nao', 'não', '0'):
            return 0
        else:
            print("    Digite S para Sim ou N para Nao.")

def pedir_numero(pergunta, minimo, maximo, tipo=float):
    """Solicita um numero dentro de um intervalo valido."""
    while True:
        try:
            valor = tipo(input(pergunta).strip().replace(',', '.'))
            if minimo <= valor <= maximo:
                return valor
            else:
                print(f"    Digite um valor entre {minimo} e {maximo}.")
        except ValueError:
            print("    Valor invalido. Digite apenas numeros.")

print(f"\n{'=' * 65}")
print("  PREVISAO INTERATIVA — Digite as informacoes do seu imovel")
print("  (Pressione Enter para confirmar cada resposta)")
print(f"{'=' * 65}\n")

continuar = True
while continuar:

    print("  Informe as caracteristicas do imovel:\n")

    area      = pedir_numero("  Area do imovel em m2 (50 a 500): ",
                             50, 500, float)
    quartos   = pedir_numero("  Numero de quartos (1 a 5): ",
                             1, 5, int)
    banheiros = pedir_numero("  Numero de banheiros (1 a 7): ",
                             1, 7, int)
    cond      = pedir_numero("  Valor do condominio em R$ (200 a 2000): ",
                             200, 2000, float)
    ano       = pedir_numero("  Ano de construcao (1980 a 2023): ",
                             1980, 2023, int)
    piscina   = sim_nao_para_int("  Tem piscina? (S/N): ")
    garagem   = sim_nao_para_int("  Tem garagem? (S/N): ")
    elevador  = sim_nao_para_int("  Tem elevador? (S/N): ")
    fechado   = sim_nao_para_int("  E condominio fechado? (S/N): ")

    imovel_usuario = {
        'Area do Imovel (m2)': area,
        'Numero de Quartos':   quartos,
        'Numero de Banheiros': banheiros,
        'Valor do Condominio': cond,
        'Ano de Construcao':   ano,
        'Tem Piscina?':        piscina,
        'Tem Garagem?':        garagem,
        'Tem Elevador?':       elevador,
        'Condominio Fechado?': fechado,
    }

    preco_usuario = prever_preco(imovel_usuario)

    print(f"\n  {'─' * 50}")
    print(f"  RESUMO DO IMOVEL INFORMADO:")
    print(f"    Area       : {area:.1f} m2")
    print(f"    Quartos    : {quartos}")
    print(f"    Banheiros  : {banheiros}")
    print(f"    Condominio : R$ {cond:,.2f}/mes")
    print(f"    Ano        : {ano}")
    print(f"    Piscina    : {'Sim' if piscina else 'Nao'}")
    print(f"    Garagem    : {'Sim' if garagem else 'Nao'}")
    print(f"    Elevador   : {'Sim' if elevador else 'Nao'}")
    print(f"    Cond.Fech. : {'Sim' if fechado else 'Nao'}")
    print(f"  {'─' * 50}")
    print(f"\n  💰 PRECO PREVISTO PELA IA: R$ {preco_usuario:,.2f}")
    print(f"  {'─' * 50}\n")

    resp = input("  Deseja prever outro imovel? (S/N): ").strip().lower()
    continuar = resp in ('s', 'sim')
    print()

print(f"\n{'=' * 65}")
print("  Obrigado por usar o Modulo 3.1!")
print("  Ate a proxima aula.")
print(f"{'=' * 65}")

# =============================================================================
#  RESUMO FINAL
# =============================================================================
print(f"""
{'=' * 65}
  RESUMO DO MODULO 3.1
{'=' * 65}

  O QUE E UMA REDE NEURAL (em 3 linhas):
  Uma rede neural e uma "fabrica" de tomada de decisoes.
  Cada camada e uma estacao que processa dados e passa para a proxima.
  Os pesos sao os "botoes de ajuste" que a IA aprende a configurar.

  NOSSA FABRICA IMOBILIARIA:
  Entrada     : {len(FEATURES)} caracteristicas do imovel
  Arquitetura : 64 → 32 → 16 → 1 neuronios
  Parametros  : {total_params:,} pesos aprendidos automaticamente
  Epocas reais: {epocas_reais} (EarlyStopping parou no momento certo)

  CORRECOES APLICADAS NESTE SCRIPT:
  1. map(Sim/Nao) → map(Sim/Nao com til) — bug silencioso corrigido
  2. Nomes das colunas renomeados para coincidir com o CSV
  3. CPF e Endereco removidos (dados pessoais irrelevantes)

  CONCEITOS APRENDIDOS:
  ReLU    = porteiro que bloqueia sinais negativos
  Dropout = treino sem titulares (evita decoreba)
  Epochs  = quantas vezes a IA releu os dados
  Batch   = quantos exemplos por correcao
  MAE     = erro medio em R$ (GPS que erra X minutos em media)
{'=' * 65}
""")
