# =============================================================================
#  MODULO 3.1 — ARQUITETURA DE REDES NEURAIS  (versao com GUI + Download)
#  Dataset: dados_falsos_Imobiliario.csv
#  Objetivo: Prever o PRECO DE UM IMOVEL
# =============================================================================
#
#  COMO RODAR LOCALMENTE:
#  1. Instale as dependências:
#     pip install tensorflow pandas scikit-learn matplotlib tqdm joblib
#     pip install tkinter   (geralmente já incluso no Python)
#  2. Execute: python modulo_3_1_rede_neural_gui.py
#  3. A interface gráfica será aberta automaticamente
#
#  O QUE FOI ADICIONADO NESTA VERSAO:
#  ✔ Interface Gráfica (Tkinter) para uso sem linha de comando
#  ✔ Salvamento automático do modelo (.keras) e dos scalers (.pkl)
#  ✔ Botão de Download que empacota tudo em um .zip para uso offline
#  ✔ Carregamento do modelo salvo (sem precisar retreinar)
# =============================================================================

# ── IMPORTACOES ORIGINAIS ──────────────────────────────────────────────────────
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

# ── IMPORTACOES ADICIONADAS — necessárias para salvar/carregar o modelo e GUI ──
import os          # manipulação de caminhos de arquivo
import io          # leitura/escrita em memória
import sys         # acesso ao interpretador Python
import zipfile     # criação do pacote .zip para download
import joblib      # salva e carrega objetos Python (scalers)
import threading   # executa o treino sem travar a interface gráfica
import tkinter as tk                            # janelas e widgets
from tkinter import ttk, filedialog, messagebox # abas, diálogos e alertas
from datetime import datetime                   # registro de data/hora no nome do arquivo

# ── SEMENTE ALEATÓRIA ─────────────────────────────────────────────────────────
tf.random.set_seed(42)
np.random.seed(42)
random.seed(42)

# =============================================================================
#  CONSTANTES GLOBAIS
# =============================================================================
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

# Nomes dos arquivos em que o modelo e os scalers serão salvos
ARQUIVO_MODELO  = "modelo_imoveis.keras"
ARQUIVO_SCALER_X = "scaler_X.pkl"
ARQUIVO_SCALER_Y = "scaler_y.pkl"

# =============================================================================
#  VARIAVEIS GLOBAIS (preenchidas após o treino ou ao carregar modelo salvo)
# =============================================================================
modelo   = None
scaler_X = None
scaler_y = None

# =============================================================================
#  FUNCOES ORIGINAIS (mantidas intactas)
# =============================================================================

def preparar_dados(caminho_csv):
    """Carrega e pré-processa o CSV. Retorna X, y prontos para o modelo."""
    df = pd.read_csv(caminho_csv)

    df.drop(columns=['CPF', 'Endereço do Imóvel'], inplace=True)

    colunas_binarias = ['Tem Piscina?', 'Tem Garagem?', 'Tem Elevador?', 'Condomínio Fechado?']
    for col in colunas_binarias:
        df[col] = df[col].map({'Sim': 1, 'Não': 0})

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

    df = pd.get_dummies(df, columns=['Tipo de Imovel', 'Tipo de Oferta'], drop_first=True)

    X = df[FEATURES].values
    y = df[TARGET].values
    return X, y, df


def construir_modelo(n_features):
    """Constrói e compila a arquitetura da rede neural (igual ao original)."""
    m = keras.Sequential(name="Fabrica_de_Avaliacao_Imobiliaria")
    m.add(layers.Input(shape=(n_features,),   name="Entrada_Dados_do_Imovel"))
    m.add(layers.Dense(64, activation='relu', name="Estacao_1_Padroes_Basicos"))
    m.add(layers.Dropout(0.2,                 name="Dropout_1_Anti_Decoreba"))
    m.add(layers.Dense(32, activation='relu', name="Estacao_2_Padroes_Complexos"))
    m.add(layers.Dropout(0.2,                 name="Dropout_2_Anti_Decoreba"))
    m.add(layers.Dense(16, activation='relu', name="Estacao_3_Refinamento_Final"))
    m.add(layers.Dense(1,  activation='linear', name="Saida_Preco_Previsto"))
    m.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='mae',
        metrics=['mse']
    )
    return m


def prever_preco(imovel_dict):
    """Recebe características do imóvel e retorna o preço previsto em R$."""
    X_novo   = np.array([[imovel_dict[f] for f in FEATURES]], dtype=np.float32)
    X_novo_n = scaler_X.transform(X_novo)
    pred_n   = modelo.predict(X_novo_n, verbose=0)[0][0]
    preco    = scaler_y.inverse_transform([[pred_n]])[0][0]
    return preco


def gerar_imovel_aleatorio(perfil='aleatorio', seed=None):
    """Cria um imóvel fictício para testes."""
    if seed is not None:
        random.seed(seed)
    if perfil == 'luxo':
        return {'Area do Imovel (m2)': round(random.uniform(350, 500), 1),
                'Numero de Quartos': random.randint(4, 5),
                'Numero de Banheiros': random.randint(4, 7),
                'Valor do Condominio': round(random.uniform(1500, 2000), 2),
                'Ano de Construcao': random.randint(2015, 2023),
                'Tem Piscina?': 1, 'Tem Garagem?': 1, 'Tem Elevador?': 1, 'Condominio Fechado?': 1}
    elif perfil == 'simples':
        return {'Area do Imovel (m2)': round(random.uniform(50, 100), 1),
                'Numero de Quartos': random.randint(1, 2),
                'Numero de Banheiros': random.randint(1, 2),
                'Valor do Condominio': round(random.uniform(200, 400), 2),
                'Ano de Construcao': random.randint(1980, 1999),
                'Tem Piscina?': 0, 'Tem Garagem?': 0, 'Tem Elevador?': 0, 'Condominio Fechado?': 0}
    elif perfil == 'medio':
        return {'Area do Imovel (m2)': round(random.uniform(150, 280), 1),
                'Numero de Quartos': random.randint(2, 3),
                'Numero de Banheiros': random.randint(2, 3),
                'Valor do Condominio': round(random.uniform(600, 1200), 2),
                'Ano de Construcao': random.randint(2000, 2015),
                'Tem Piscina?': random.randint(0, 1),
                'Tem Garagem?': 1,
                'Tem Elevador?': random.randint(0, 1),
                'Condominio Fechado?': random.randint(0, 1)}
    else:
        return {'Area do Imovel (m2)': round(random.uniform(50, 500), 1),
                'Numero de Quartos': random.randint(1, 5),
                'Numero de Banheiros': random.randint(1, 7),
                'Valor do Condominio': round(random.uniform(200, 2000), 2),
                'Ano de Construcao': random.randint(1980, 2023),
                'Tem Piscina?': random.randint(0, 1),
                'Tem Garagem?': random.randint(0, 1),
                'Tem Elevador?': random.randint(0, 1),
                'Condominio Fechado?': random.randint(0, 1)}


# =============================================================================
#  FUNCOES ADICIONADAS — SALVAR / CARREGAR / EMPACOTAR MODELO
# =============================================================================

def salvar_modelo_e_scalers(pasta_destino="."):
    """
    [NOVO] Salva o modelo Keras e os dois scalers na pasta indicada.

    Arquivos gerados:
      - modelo_imoveis.keras  → arquitetura + pesos da rede neural
      - scaler_X.pkl          → normalizador das features (entrada)
      - scaler_y.pkl          → normalizador do preço (saída)

    Esses três arquivos são necessários para usar o modelo sem retreinar.
    """
    if modelo is None or scaler_X is None or scaler_y is None:
        raise RuntimeError("Treine ou carregue um modelo antes de salvar.")

    caminho_modelo   = os.path.join(pasta_destino, ARQUIVO_MODELO)
    caminho_scaler_x = os.path.join(pasta_destino, ARQUIVO_SCALER_X)
    caminho_scaler_y = os.path.join(pasta_destino, ARQUIVO_SCALER_Y)

    modelo.save(caminho_modelo)                # salva no formato nativo do Keras
    joblib.dump(scaler_X, caminho_scaler_x)    # serializa o scaler das features
    joblib.dump(scaler_y, caminho_scaler_y)    # serializa o scaler do target

    return caminho_modelo, caminho_scaler_x, caminho_scaler_y


def carregar_modelo_salvo(pasta_origem="."):
    """
    [NOVO] Carrega um modelo previamente salvo — sem necessidade de retreinar.

    Retorna True se carregado com sucesso, False se os arquivos não forem encontrados.
    Os objetos globais `modelo`, `scaler_X` e `scaler_y` são preenchidos.
    """
    global modelo, scaler_X, scaler_y

    caminho_modelo   = os.path.join(pasta_origem, ARQUIVO_MODELO)
    caminho_scaler_x = os.path.join(pasta_origem, ARQUIVO_SCALER_X)
    caminho_scaler_y = os.path.join(pasta_origem, ARQUIVO_SCALER_Y)

    # Verifica se todos os arquivos necessários existem antes de carregar
    if not all(os.path.exists(p) for p in [caminho_modelo, caminho_scaler_x, caminho_scaler_y]):
        return False

    modelo   = keras.models.load_model(caminho_modelo)  # carrega arquitetura + pesos
    scaler_X = joblib.load(caminho_scaler_x)             # recupera o normalizador
    scaler_y = joblib.load(caminho_scaler_y)             # recupera o normalizador
    return True


def criar_zip_para_download(caminho_destino):
    """
    [NOVO] Empacota o modelo, scalers e o próprio script em um arquivo .zip.

    O usuário pode levar este .zip para qualquer computador e usar o modelo
    sem precisar do CSV ou de retreinar. Basta descompactar e rodar o script.

    Conteúdo do .zip:
      modelo_imoveis.keras   → a rede neural treinada
      scaler_X.pkl           → normalizador das features
      scaler_y.pkl           → normalizador do preço
      modulo_3_1_rede_neural_gui.py  → este script (para uso local)
      LEIA_ME.txt            → instruções rápidas
    """
    if modelo is None:
        raise RuntimeError("Treine ou carregue um modelo antes de fazer o download.")

    # Primeiro salva os arquivos do modelo na pasta atual
    salvar_modelo_e_scalers(".")

    leia_me = (
        "=== MODELO DE PREVISÃO IMOBILIÁRIA — INSTRUÇÕES RÁPIDAS ===\n\n"
        "Para usar este modelo no seu computador:\n\n"
        "1. Instale as dependências:\n"
        "   pip install tensorflow pandas scikit-learn matplotlib joblib\n\n"
        "2. Execute o script:\n"
        "   python modulo_3_1_rede_neural_gui.py\n\n"
        "3. Na aba 'Prever Imóvel', clique em 'Carregar Modelo Salvo'\n"
        "   (não é necessário o CSV nem retreinar)\n\n"
        "Arquivos incluídos:\n"
        "  modelo_imoveis.keras  — arquitetura e pesos da rede neural\n"
        "  scaler_X.pkl          — normalizador das features\n"
        "  scaler_y.pkl          — normalizador do preço\n"
    )

    # Cria o arquivo .zip e adiciona cada arquivo ao pacote
    with zipfile.ZipFile(caminho_destino, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(ARQUIVO_MODELO)              # modelo treinado
        zf.write(ARQUIVO_SCALER_X)            # scaler das features
        zf.write(ARQUIVO_SCALER_Y)            # scaler do target
        zf.writestr("LEIA_ME.txt", leia_me)   # instruções embutidas no zip

        # Inclui o próprio script para facilitar a reprodução em outro PC
        script_atual = os.path.abspath(__file__)
        if os.path.exists(script_atual):
            zf.write(script_atual, os.path.basename(script_atual))

    return caminho_destino


# =============================================================================
#  INTERFACE GRÁFICA (TKINTER) — ADICIONADA
# =============================================================================

class AplicativoImoveis(tk.Tk):
    """
    [NOVO] Janela principal da aplicação.

    Estrutura de abas:
      Aba 1 — Treinar Modelo  : seleciona CSV, configura e inicia o treino
      Aba 2 — Prever Imóvel   : preenche características e obtém o preço
      Aba 3 — Download        : empacota e baixa o modelo treinado
    """

    def __init__(self):
        super().__init__()
        self.title("Avaliador de Imóveis com IA — Módulo 3.1")
        self.geometry("720x620")
        self.resizable(True, True)
        self._configurar_estilo()
        self._construir_interface()

    # ── Estilos visuais ────────────────────────────────────────────────────────
    def _configurar_estilo(self):
        """Define cores e fontes da interface."""
        self.configure(bg="#1e1e2e")
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        # Fundo das abas
        estilo.configure("TNotebook",        background="#1e1e2e", borderwidth=0)
        estilo.configure("TNotebook.Tab",    background="#2d2d44", foreground="#cdd6f4",
                         padding=[14, 6], font=("Segoe UI", 10, "bold"))
        estilo.map("TNotebook.Tab",          background=[("selected", "#89b4fa")])
        # Frames internos
        estilo.configure("TFrame",           background="#1e1e2e")
        estilo.configure("TLabel",           background="#1e1e2e", foreground="#cdd6f4",
                         font=("Segoe UI", 10))
        estilo.configure("Header.TLabel",    background="#1e1e2e", foreground="#89b4fa",
                         font=("Segoe UI", 13, "bold"))
        estilo.configure("Result.TLabel",    background="#1e1e2e", foreground="#a6e3a1",
                         font=("Segoe UI", 16, "bold"))
        estilo.configure("TButton",          background="#89b4fa", foreground="#1e1e2e",
                         font=("Segoe UI", 10, "bold"), padding=8)
        estilo.map("TButton",                background=[("active", "#74c7ec")])
        estilo.configure("TEntry",           fieldbackground="#313244", foreground="#cdd6f4",
                         font=("Segoe UI", 10))
        estilo.configure("TCheckbutton",     background="#1e1e2e", foreground="#cdd6f4",
                         font=("Segoe UI", 10))
        estilo.configure("TProgressbar",     troughcolor="#313244", background="#89b4fa")
        estilo.configure("TSpinbox",         fieldbackground="#313244", foreground="#cdd6f4",
                         font=("Segoe UI", 10))

    # ── Montagem das abas ──────────────────────────────────────────────────────
    def _construir_interface(self):
        """Cria o notebook com as três abas."""
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        aba_treino  = ttk.Frame(notebook)
        aba_prever  = ttk.Frame(notebook)
        aba_download = ttk.Frame(notebook)

        notebook.add(aba_treino,   text="  🎓 Treinar Modelo  ")
        notebook.add(aba_prever,   text="  🏠 Prever Imóvel  ")
        notebook.add(aba_download, text="  💾 Download  ")

        self._montar_aba_treino(aba_treino)
        self._montar_aba_prever(aba_prever)
        self._montar_aba_download(aba_download)

    # ── ABA 1: Treinar ─────────────────────────────────────────────────────────
    def _montar_aba_treino(self, pai):
        """Aba de configuração e execução do treinamento."""
        ttk.Label(pai, text="Treinamento da Rede Neural", style="Header.TLabel"
                  ).pack(pady=(18, 6))

        # Seleção do CSV
        frame_csv = ttk.Frame(pai)
        frame_csv.pack(fill="x", padx=20, pady=4)
        ttk.Label(frame_csv, text="Arquivo CSV:").pack(side="left")
        self.var_csv = tk.StringVar(value="Nenhum arquivo selecionado")
        ttk.Label(frame_csv, textvariable=self.var_csv,
                  foreground="#fab387").pack(side="left", padx=8)
        ttk.Button(frame_csv, text="Selecionar CSV",
                   command=self._selecionar_csv).pack(side="right")

        # Configurações de treino
        frame_cfg = ttk.Frame(pai)
        frame_cfg.pack(fill="x", padx=20, pady=8)
        ttk.Label(frame_cfg, text="Épocas máximas:").grid(row=0, column=0, sticky="w", padx=4)
        self.var_epocas = tk.IntVar(value=60)
        ttk.Spinbox(frame_cfg, from_=10, to=300, textvariable=self.var_epocas,
                    width=6).grid(row=0, column=1, padx=8)
        ttk.Label(frame_cfg, text="Batch size:").grid(row=0, column=2, sticky="w", padx=4)
        self.var_batch = tk.IntVar(value=256)
        ttk.Spinbox(frame_cfg, from_=32, to=1024, textvariable=self.var_batch,
                    increment=32, width=6).grid(row=0, column=3, padx=8)

        # Barra de progresso
        self.barra_treino = ttk.Progressbar(pai, mode="determinate", style="TProgressbar")
        self.barra_treino.pack(fill="x", padx=20, pady=8)

        # Log de saída
        self.txt_log = tk.Text(pai, height=10, bg="#181825", fg="#cdd6f4",
                               font=("Consolas", 9), relief="flat", wrap="word")
        self.txt_log.pack(fill="both", expand=True, padx=20, pady=4)

        # Botão de treinar
        ttk.Button(pai, text="▶  Iniciar Treinamento",
                   command=self._iniciar_treino).pack(pady=10)

    # ── ABA 2: Prever ──────────────────────────────────────────────────────────
    def _montar_aba_prever(self, pai):
        """Aba com formulário para prever o preço de um imóvel."""
        ttk.Label(pai, text="Previsão de Preço", style="Header.TLabel"
                  ).pack(pady=(18, 8))

        # Botão para carregar modelo salvo anteriormente
        ttk.Button(pai, text="📂 Carregar Modelo Salvo",
                   command=self._carregar_modelo_gui).pack(pady=(0, 10))

        # Formulário de entrada
        frame_form = ttk.Frame(pai)
        frame_form.pack(padx=30, fill="x")

        campos = [
            ("Área (m²):",            "area",     "150",    50,   500),
            ("Quartos:",               "quartos",  "2",      1,    5  ),
            ("Banheiros:",             "banheiros","2",      1,    7  ),
            ("Condomínio (R$/mês):",   "cond",     "800",    200,  2000),
            ("Ano de construção:",     "ano",      "2010",   1980, 2023),
        ]

        self.vars_entry = {}
        for i, (label, chave, padrao, vmin, vmax) in enumerate(campos):
            ttk.Label(frame_form, text=label).grid(row=i, column=0, sticky="w", pady=3)
            var = tk.StringVar(value=padrao)
            ttk.Entry(frame_form, textvariable=var, width=12).grid(
                row=i, column=1, sticky="w", padx=12)
            # Exibe o intervalo válido como dica
            ttk.Label(frame_form, text=f"({vmin}–{vmax})",
                      foreground="#6c7086").grid(row=i, column=2, sticky="w")
            self.vars_entry[chave] = var

        # Checkboxes para características binárias
        self.vars_check = {}
        checks = [("Piscina", "piscina"), ("Garagem", "garagem"),
                  ("Elevador", "elevador"), ("Condomínio Fechado", "fechado")]
        frame_checks = ttk.Frame(pai)
        frame_checks.pack(pady=8)
        for i, (label, chave) in enumerate(checks):
            var = tk.BooleanVar()
            ttk.Checkbutton(frame_checks, text=label, variable=var).grid(
                row=0, column=i, padx=12)
            self.vars_check[chave] = var

        ttk.Button(pai, text="💰 Calcular Preço",
                   command=self._calcular_preco).pack(pady=8)

        # Resultado
        self.var_resultado = tk.StringVar(value="—")
        ttk.Label(pai, textvariable=self.var_resultado, style="Result.TLabel"
                  ).pack(pady=6)

    # ── ABA 3: Download ────────────────────────────────────────────────────────
    def _montar_aba_download(self, pai):
        """[NOVO] Aba para salvar e fazer download do modelo treinado."""
        ttk.Label(pai, text="Salvar e Baixar o Modelo", style="Header.TLabel"
                  ).pack(pady=(30, 10))

        info = (
            "Após o treinamento, use esta aba para salvar o modelo\n"
            "e distribuí-lo como um arquivo .zip.\n\n"
            "O pacote inclui:\n"
            "  • modelo_imoveis.keras   (pesos da rede neural)\n"
            "  • scaler_X.pkl           (normalizador das entradas)\n"
            "  • scaler_y.pkl           (normalizador do preço)\n"
            "  • modulo_3_1_rede_neural_gui.py   (este script)\n"
            "  • LEIA_ME.txt            (instruções de uso)"
        )
        ttk.Label(pai, text=info, justify="left", foreground="#a6adc8"
                  ).pack(padx=30)

        # Botão: salvar apenas os arquivos individuais
        ttk.Button(pai, text="💾 Salvar Arquivos do Modelo",
                   command=self._salvar_arquivos).pack(pady=(20, 6))

        # Botão: criar .zip e escolher onde salvar
        ttk.Button(pai, text="📦 Baixar como .zip",
                   command=self._baixar_zip).pack(pady=6)

        self.lbl_status_download = ttk.Label(pai, text="", foreground="#a6e3a1")
        self.lbl_status_download.pack(pady=8)

    # ── Handlers dos botões ────────────────────────────────────────────────────

    def _selecionar_csv(self):
        """Abre diálogo para o usuário escolher o arquivo CSV."""
        caminho = filedialog.askopenfilename(
            title="Selecione o CSV de imóveis",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if caminho:
            self.var_csv.set(caminho)

    def _log(self, texto):
        """[NOVO] Adiciona uma linha ao log de treino na aba 1."""
        self.txt_log.insert("end", texto + "\n")
        self.txt_log.see("end")
        self.update_idletasks()

    def _iniciar_treino(self):
        """
        [NOVO] Executa o treino em uma thread separada para não travar a janela.
        Usa threading para que a barra de progresso e o log sejam atualizados
        em tempo real enquanto a rede neural aprende.
        """
        caminho = self.var_csv.get()
        if not os.path.exists(caminho):
            messagebox.showerror("Erro", "Selecione um arquivo CSV válido antes de treinar.")
            return
        # Inicia o treino em uma thread separada
        t = threading.Thread(target=self._executar_treino, args=(caminho,), daemon=True)
        t.start()

    def _executar_treino(self, caminho_csv):
        """
        [NOVO] Lógica de treino executada na thread secundária.

        Fluxo:
          1. Carrega e prepara os dados (igual ao original)
          2. Normaliza com MinMaxScaler
          3. Treina com EarlyStopping
          4. Avalia no conjunto de teste
          5. Salva automaticamente o modelo e os scalers
        """
        global modelo, scaler_X, scaler_y

        try:
            self._log("Carregando dados...")
            X, y, df = preparar_dados(caminho_csv)
            self._log(f"  {len(df):,} imóveis | {len(FEATURES)} features")

            # Divisão treino/teste
            X_treino, X_teste, y_treino, y_teste = train_test_split(
                X, y, test_size=0.20, random_state=42)

            # Normalização (scaler aprende SOMENTE no treino)
            scaler_X = MinMaxScaler()
            scaler_y = MinMaxScaler()
            X_treino_n = scaler_X.fit_transform(X_treino)
            y_treino_n = scaler_y.fit_transform(y_treino.reshape(-1, 1)).flatten()
            X_teste_n  = scaler_X.transform(X_teste)
            y_teste_n  = scaler_y.transform(y_teste.reshape(-1, 1)).flatten()

            # Construção do modelo
            modelo = construir_modelo(len(FEATURES))
            self._log(f"  Parâmetros: {modelo.count_params():,}")

            EPOCAS     = self.var_epocas.get()
            BATCH_SIZE = self.var_batch.get()
            self.barra_treino["maximum"] = EPOCAS
            self.barra_treino["value"]   = 0

            # Callback personalizado que atualiza a barra e o log
            class CallbackGUI(keras.callbacks.Callback):
                """[NOVO] Conecta os eventos de treino Keras à interface gráfica."""
                def __init__(cb_self):
                    super().__init__()

                def on_epoch_end(cb_self, epoch, logs=None):
                    logs = logs or {}
                    # Atualiza barra de progresso
                    self.barra_treino["value"] = epoch + 1
                    self.update_idletasks()
                    # Exibe métricas no log a cada 5 épocas
                    if (epoch + 1) % 5 == 0:
                        self._log(
                            f"  Época {epoch+1:>3} | "
                            f"Treino: {logs.get('loss', 0):.4f} | "
                            f"Val: {logs.get('val_loss', 0):.4f}"
                        )

            self._log(f"\nIniciando treino ({EPOCAS} épocas máx.)...")
            historico = modelo.fit(
                X_treino_n, y_treino_n,
                validation_split=0.15,
                epochs=EPOCAS,
                batch_size=BATCH_SIZE,
                callbacks=[
                    CallbackGUI(),
                    keras.callbacks.EarlyStopping(
                        monitor='val_loss', patience=12,
                        restore_best_weights=True, verbose=0)
                ],
                verbose=0
            )

            epocas_reais = len(historico.history['loss'])
            self._log(f"\nTreino concluído em {epocas_reais} épocas.")

            # Avaliação no conjunto de teste
            mae_norm = modelo.evaluate(X_teste_n, y_teste_n, verbose=0)[0]
            # Converte MAE normalizado de volta para R$
            escala = scaler_y.data_range_[0]
            mae_rs = mae_norm * escala
            self._log(f"MAE no teste: R$ {mae_rs:,.0f}")

            # Salva automaticamente o modelo e os scalers após o treino
            salvar_modelo_e_scalers(".")
            self._log("\n✔ Modelo salvo automaticamente!")
            self._log(f"  → {ARQUIVO_MODELO}")
            self._log(f"  → {ARQUIVO_SCALER_X}")
            self._log(f"  → {ARQUIVO_SCALER_Y}")
            self._log("\nVá para a aba 'Prever Imóvel' para testar.")

        except Exception as e:
            self._log(f"\nERRO: {e}")

    def _carregar_modelo_gui(self):
        """
        [NOVO] Carrega o modelo previamente salvo.
        Tenta carregar da pasta atual; se não encontrar, abre diálogo
        para o usuário escolher a pasta onde os arquivos estão.
        """
        if carregar_modelo_salvo("."):
            messagebox.showinfo("Sucesso", "Modelo carregado com sucesso!")
        else:
            pasta = filedialog.askdirectory(title="Onde estão os arquivos do modelo?")
            if pasta and carregar_modelo_salvo(pasta):
                messagebox.showinfo("Sucesso", "Modelo carregado!")
            else:
                messagebox.showerror("Erro",
                    "Arquivos não encontrados. Treine o modelo primeiro.")

    def _calcular_preco(self):
        """Lê o formulário e exibe o preço previsto."""
        if modelo is None:
            messagebox.showwarning("Aviso",
                "Nenhum modelo disponível.\n"
                "Treine ou carregue um modelo salvo primeiro.")
            return
        try:
            imovel = {
                'Area do Imovel (m2)':  float(self.vars_entry['area'].get()),
                'Numero de Quartos':    int(self.vars_entry['quartos'].get()),
                'Numero de Banheiros':  int(self.vars_entry['banheiros'].get()),
                'Valor do Condominio':  float(self.vars_entry['cond'].get()),
                'Ano de Construcao':    int(self.vars_entry['ano'].get()),
                'Tem Piscina?':         int(self.vars_check['piscina'].get()),
                'Tem Garagem?':         int(self.vars_check['garagem'].get()),
                'Tem Elevador?':        int(self.vars_check['elevador'].get()),
                'Condominio Fechado?':  int(self.vars_check['fechado'].get()),
            }
            preco = prever_preco(imovel)
            self.var_resultado.set(f"R$ {preco:,.2f}")
        except ValueError:
            messagebox.showerror("Erro de entrada",
                "Verifique os valores digitados. Use ponto (.) para decimais.")

    def _salvar_arquivos(self):
        """[NOVO] Salva modelo e scalers na pasta que o usuário escolher."""
        if modelo is None:
            messagebox.showwarning("Aviso", "Treine um modelo antes de salvar.")
            return
        pasta = filedialog.askdirectory(title="Onde salvar os arquivos?")
        if pasta:
            salvar_modelo_e_scalers(pasta)
            self.lbl_status_download.config(
                text=f"✔ Arquivos salvos em: {pasta}")

    def _baixar_zip(self):
        """
        [NOVO] Cria o arquivo .zip com o modelo completo e pede ao usuário
        onde salvá-lo. Inclui todos os arquivos necessários para uso offline.
        """
        if modelo is None:
            messagebox.showwarning("Aviso", "Treine um modelo antes de baixar.")
            return

        # Gera nome padrão com data/hora para evitar sobrescrita acidental
        nome_padrao = f"modelo_imoveis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        caminho = filedialog.asksaveasfilename(
            title="Salvar .zip do modelo",
            defaultextension=".zip",
            initialfile=nome_padrao,
            filetypes=[("ZIP files", "*.zip")]
        )
        if caminho:
            try:
                criar_zip_para_download(caminho)
                self.lbl_status_download.config(
                    text=f"✔ Download salvo em:\n{caminho}")
                messagebox.showinfo("Sucesso",
                    f"Arquivo .zip criado com sucesso!\n\n{caminho}")
            except Exception as e:
                messagebox.showerror("Erro", str(e))


# =============================================================================
#  PONTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    # Tenta carregar um modelo previamente salvo ao iniciar a aplicação.
    # Se não existir, o usuário precisará treinar pelo menu "Treinar Modelo".
    carregar_modelo_salvo(".")

    # Inicia a interface gráfica
    app = AplicativoImoveis()
    app.mainloop()
