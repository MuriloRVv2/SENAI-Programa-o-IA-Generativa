# ╔══════════════════════════════════════════════════════════╗
# ║  🍽️  EXERCICIO 3 — Bot da Cantina Escolar              ║
# ║  Nivel: Dificil  |  Base: Exemplo 04 (Pizza multi-turn) ║
# ╚══════════════════════════════════════════════════════════╝
#
# ════════════════════════════════════════════════════════════
#  GABARITO — resultado esperado apos o uso do prompt
# ════════════════════════════════════════════════════════════
#
# CONTEXTO DO EXERCICIO:
#   A cantina da escola quer modernizar o atendimento.
#   Os alunos poderao fazer pedidos pelo chatbot antes do
#   intervalo e retirar na hora certa, sem fila!
#
# O QUE O BOT DEVE FAZER (fluxo multi-turn de 5 etapas):
#   1. Mostrar cardapio e perguntar o que o aluno quer
#   2. Perguntar a quantidade (1 a 5 itens)
#   3. Pedir o numero da turma para entrega
#   4. Pedir a forma de pagamento (dinheiro, pix, cartao)
#   5. Confirmar e gerar numero de pedido com total
#
# PROMPT QUE GEROU ESTE CODIGO:
#   "Crie um chatbot em Python usando a classe MiniDialogflowPro
#    (com TF-IDF) para o sistema de pedidos da Cantina Escolar.
#    Cardapio: x-salada R$12, misto R$8, suco R$5, agua R$3, salgado R$4.
#    O fluxo deve ter 5 etapas com contextos diferentes:
#    1. Boas-vindas: mostra cardapio e pergunta o item
#    2. Escolha do item: registra e pergunta quantidade (1 a 5)
#    3. Quantidade: calcula subtotal e pergunta turma
#    4. Turma: registra (ex: 1A, 2B) e pergunta pagamento
#    5. Pagamento: gera pedido com numero aleatorio e total
#    Inclua funcoes para cada etapa, calculo automatico do total,
#    a classe MiniDialogflowPro completa. Ao final chame bot.chat()."
#
# INSTALACAO: pip install colorama scikit-learn
# COMO RODAR: python ex03_cantina.py
# ════════════════════════════════════════════════════════════

import re
import math
import random
from colorama import Fore, Style, init
init(autoreset=True)


class MiniDialogflowPro:
    """Dialogflow com TF-IDF + context-aware fallback."""

    def __init__(self, nome):
        self.nome = nome
        self.intents = {}
        self.contexto = None
        self.dados = {}
        self._idf = {}

    def treinar_intent(self, nome, frases, respostas,
                       entidades=None, exige_ctx=None,
                       gera_ctx=None, acao=None):
        self.intents[nome] = {
            "frases"   : [f.lower().strip() for f in frases],
            "respostas": respostas,
            "entidades": entidades or [],
            "exige_ctx": exige_ctx,
            "gera_ctx" : gera_ctx,
            "acao"     : acao,
        }
        self._recalcular_idf()

    def _tok(self, t): return re.findall(r"[a-z0-9]+", t.lower())

    def _recalcular_idf(self):
        docs = [set(self._tok(f)) for i in self.intents.values() for f in i["frases"]]
        if not docs: return
        N = len(docs); freq = {}
        for d in docs:
            for p in d: freq[p] = freq.get(p, 0) + 1
        self._idf = {p: math.log(N / (c + 1)) for p, c in freq.items()}

    def _tfidf(self, t):
        toks = self._tok(t); tf = {}
        for tk in toks: tf[tk] = tf.get(tk, 0) + 1 / max(len(toks), 1)
        return {tk: v * self._idf.get(tk, 0) for tk, v in tf.items()}

    def _cos(self, v1, v2):
        w = set(v1) | set(v2)
        d = sum(v1.get(p, 0) * v2.get(p, 0) for p in w)
        m1 = math.sqrt(sum(x**2 for x in v1.values()))
        m2 = math.sqrt(sum(x**2 for x in v2.values()))
        return d / (m1 * m2) if m1 and m2 else 0.0

    def _si(self, vm, frases):
        return max((self._cos(vm, self._tfidf(f)) for f in frases), default=0.0)

    def detectar(self, msg):
        ml = msg.lower().strip(); vm = self._tfidf(ml)
        melhor, score = None, 0.0
        for nome, intent in self.intents.items():
            if intent["exige_ctx"] and self.contexto != intent["exige_ctx"]: continue
            s = self._si(vm, intent["frases"])
            if s > score: score, melhor = s, nome
        if not (melhor and score >= 0.12):
            if self.contexto:
                cands = [(n, i) for n, i in self.intents.items()
                         if i["exige_ctx"] == self.contexto]
                if cands:
                    melhor = max(cands, key=lambda x: self._si(vm, x[1]["frases"]))[0]
                    score = 0.01
                else: melhor = None
            else: melhor = None
        if melhor:
            intent = self.intents[melhor]
            if intent["gera_ctx"] is not None: self.contexto = intent["gera_ctx"]
            ents = self._extrair(ml, intent["entidades"]); self.dados.update(ents)
            resp = random.choice(intent["respostas"])
            for k, v in {**self.dados, **ents}.items(): resp = resp.replace(f"{{{k}}}", str(v))
            if intent["acao"]:
                r2 = intent["acao"](ml, self.dados, {})
                if r2: resp = r2
        else:
            melhor, score, ents = "fallback", 0.0, {}
            resp = random.choice([
                "Nao entendi. Pode repetir?",
                "Hmm, pode reformular?",
            ])
        return {"intent": melhor, "score": round(score, 2),
                "resposta": resp, "contexto": self.contexto}

    def _extrair(self, msg, defs):
        r = {}
        for d in defs:
            for v in d.get("valores", []):
                if v.lower() in msg: r[d["nome"]] = v; break
            if d.get("regex") and d["nome"] not in r:
                m = re.search(d["regex"], msg, re.IGNORECASE)
                if m: r[d["nome"]] = m.group()
        return r

    def resetar(self): self.contexto = None; self.dados = {}

    def chat(self, debug=True):
        print(f"\n{Fore.CYAN}{'='*54}")
        print(f"  🍽️  Cantina Escolar — Pedidos Online")
        print(f"  'sair' = encerrar | 'reset' = novo pedido")
        print(f"{'='*54}{Style.RESET_ALL}\n")
        while True:
            try:
                user = input(f"{Fore.GREEN}Voce >>> {Style.RESET_ALL}").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not user: continue
            if user.lower() == "sair":
                print(f"\n{Fore.CYAN}  Ate mais! Bom apetite! 🍽️{Style.RESET_ALL}")
                break
            if user.lower() == "reset":
                self.resetar(); pedido.clear()
                print(f"{Fore.YELLOW}  [Novo pedido iniciado]{Style.RESET_ALL}\n")
                continue
            r = self.detectar(user)
            print(f"{Fore.BLUE}Bot  >>> {r['resposta']}{Style.RESET_ALL}")
            if debug:
                print(f"{Fore.WHITE}         [intent: {r['intent']} | "
                      f"certeza: {r['score']:.0%} | "
                      f"contexto: {r['contexto'] or 'nenhum'}]{Style.RESET_ALL}")
            print()

    def simular(self, msgs):
        for msg in msgs:
            r = self.detectar(msg)
            print(f"  Aluno: {Fore.GREEN}{msg}{Style.RESET_ALL}")
            print(f"  Bot  : {Fore.BLUE}{r['resposta'][:85]}{'...' if len(r['resposta'])>85 else ''}{Style.RESET_ALL}\n")


# ════════════════════════════════════════════════════════════
#  CARDAPIO DA CANTINA
# ════════════════════════════════════════════════════════════

CARDAPIO = {
    "x-salada": 12.00,
    "misto"   : 8.00,
    "suco"    : 5.00,
    "agua"    : 3.00,
    "salgado" : 4.00,
}

CARDAPIO_TEXTO = "\n".join(
    f"  {item.title():<12} R$ {preco:.2f}"
    for item, preco in CARDAPIO.items()
)

FORMAS_PAGTO = ["dinheiro", "pix", "cartao", "debito", "credito"]

pedido = {}


# ════════════════════════════════════════════════════════════
#  FUNCOES DE CADA ETAPA (Fulfillment)
# ════════════════════════════════════════════════════════════

def mostrar_cardapio(msg, dados, ctx):
    """ETAPA 1: Mostra o cardapio e pede a escolha."""
    pedido.clear()
    return (f"Ola! Bem-vindo a Cantina! 🍽️\n\n"
            f"Cardapio de hoje:\n{CARDAPIO_TEXTO}\n\n"
            f"O que voce vai querer hoje?")


def registrar_item(msg, dados, ctx):
    """ETAPA 2: Identifica o item escolhido e pede quantidade."""
    item_escolhido = None
    for item in CARDAPIO:
        if item in msg.lower():
            item_escolhido = item
            break

    if not item_escolhido:
        return (f"Item nao encontrado no cardapio!\n"
                f"Temos: {', '.join(CARDAPIO.keys())}")

    pedido["item"]  = item_escolhido
    pedido["preco"] = CARDAPIO[item_escolhido]

    return (f"{item_escolhido.title()} selecionado! ✓\n"
            f"Preco unitario: R$ {pedido['preco']:.2f}\n\n"
            f"Quantas unidades? (minimo 1, maximo 5)")


def registrar_quantidade(msg, dados, ctx):
    """ETAPA 3: Registra quantidade, calcula subtotal, pede turma."""
    numeros = re.findall(r"\d+", msg)
    if not numeros:
        return "Me diz um numero de 1 a 5!"

    qtd = int(numeros[0])
    if not (1 <= qtd <= 5):
        return "Quantidade deve ser entre 1 e 5!"

    pedido["quantidade"] = qtd
    subtotal = qtd * pedido["preco"]
    pedido["subtotal"] = subtotal

    return (f"{qtd} unidade(s) de {pedido['item'].title()} ✓\n"
            f"Subtotal: R$ {subtotal:.2f}\n\n"
            f"Qual e a sua turma?\n"
            f"(ex: 1A, 2B, 3C — para entregar na hora certa)")


def registrar_turma(msg, dados, ctx):
    """ETAPA 4: Registra turma e pede forma de pagamento."""
    # Aceita formatos como: 1A, 2B, 3A, 1B, turma 2C
    turma_match = re.search(r"\d[A-Ca-c]", msg, re.IGNORECASE)
    if turma_match:
        pedido["turma"] = turma_match.group().upper()
    else:
        # Tenta extrair qualquer turma mencionada
        pedido["turma"] = msg.strip().upper()[:4]

    return (f"Turma {pedido['turma']} anotada! ✓\n\n"
            f"Forma de pagamento?\n"
            f"  💵 Dinheiro\n"
            f"  📱 PIX\n"
            f"  💳 Cartao (debito ou credito)")


def registrar_pagamento(msg, dados, ctx):
    """ETAPA 5: Registra pagamento e confirma o pedido completo."""
    forma = "dinheiro"  # padrao
    for f in FORMAS_PAGTO:
        if f in msg.lower():
            forma = f
            break

    pedido["pagamento"] = forma.title()

    # Gera numero do pedido
    numero_pedido = f"CAN-{random.randint(1000, 9999)}"
    pedido["numero"] = numero_pedido

    emoji_pagto = {"Dinheiro": "💵", "Pix": "📱",
                   "Cartao": "💳", "Debito": "💳", "Credito": "💳"}
    emoji = emoji_pagto.get(pedido["pagamento"], "💰")

    return (f"✅ PEDIDO CONFIRMADO!\n\n"
            f"  Numero : {numero_pedido}\n"
            f"  Item   : {pedido.get('item', '?').title()}\n"
            f"  Qtd    : {pedido.get('quantidade', '?')}x\n"
            f"  Total  : R$ {pedido.get('subtotal', 0):.2f}\n"
            f"  Turma  : {pedido.get('turma', '?')}\n"
            f"  Pagto  : {emoji} {pedido.get('pagamento', '?')}\n\n"
            f"Retire no balcao durante o intervalo!\n"
            f"Guarde o numero: {numero_pedido}")


def ver_cardapio_rapido(msg, dados, ctx):
    """Mostra o cardapio em qualquer momento."""
    return f"Cardapio:\n{CARDAPIO_TEXTO}"


# ════════════════════════════════════════════════════════════
#  CONFIGURACAO DO BOT
# ════════════════════════════════════════════════════════════

bot = MiniDialogflowPro("CantinaBot")

# ETAPA 1: Iniciar pedido → mostra cardapio
bot.treinar_intent(
    nome="iniciar_pedido",
    frases=["quero pedir", "fazer pedido", "oi cantina", "ola",
            "quero lanchar", "cardapio", "quero comprar",
            "bom dia cantina", "preciso de lanche"],
    respostas=["Carregando cardapio..."],
    gera_ctx="escolhendo_item",
    acao=mostrar_cardapio
)

# ETAPA 2: Escolher item → pede quantidade
bot.treinar_intent(
    nome="escolher_item",
    frases=list(CARDAPIO.keys()) + [
        "quero o", "quero um", "quero uma", "me da",
        "vou querer", "x salada", "x-salada"
    ],
    respostas=["Registrando item..."],
    exige_ctx="escolhendo_item",
    gera_ctx="escolhendo_quantidade",
    acao=registrar_item
)

# ETAPA 3: Quantidade → pede turma
bot.treinar_intent(
    nome="escolher_quantidade",
    frases=["1", "2", "3", "4", "5", "um", "dois", "tres",
            "uma unidade", "duas unidades", "quero"],
    respostas=["Registrando quantidade..."],
    exige_ctx="escolhendo_quantidade",
    gera_ctx="informando_turma",
    acao=registrar_quantidade
)

# ETAPA 4: Turma → pede pagamento
bot.treinar_intent(
    nome="informar_turma",
    frases=["turma", "1a", "1b", "1c", "2a", "2b", "2c",
            "3a", "3b", "3c", "minha turma e", "sou da"],
    respostas=["Registrando turma..."],
    exige_ctx="informando_turma",
    gera_ctx="escolhendo_pagamento",
    acao=registrar_turma
)

# ETAPA 5: Pagamento → confirma pedido
bot.treinar_intent(
    nome="escolher_pagamento",
    frases=FORMAS_PAGTO + ["pago com", "forma de pagamento",
                            "vou pagar", "aceita pix"],
    respostas=["Processando pagamento..."],
    exige_ctx="escolhendo_pagamento",
    gera_ctx=None,
    acao=registrar_pagamento
)

# Intent extra: ver cardapio a qualquer momento
bot.treinar_intent(
    nome="ver_cardapio",
    frases=["ver cardapio", "mostra cardapio", "o que tem",
            "quais opcoes", "quanto custa"],
    respostas=["Cardapio..."],
    acao=ver_cardapio_rapido
)

# Intent: despedida
bot.treinar_intent(
    nome="despedida",
    frases=["tchau", "obrigado", "valeu", "ate mais", "ja pedi"],
    respostas=["Bom apetite! 🍽️", "Ate mais! Aproveite o lanche!"]
)


# ════════════════════════════════════════════════════════════
#  DEMONSTRACAO AUTOMATICA
# ════════════════════════════════════════════════════════════

print(f"\n{Fore.YELLOW}{'='*54}")
print("  EXERCICIO 3 — Bot da Cantina Escolar")
print("  Demonstracao do fluxo completo")
print(f"{'='*54}{Style.RESET_ALL}\n")

bot.simular([
    "oi quero pedir",
    "x-salada",
    "2",
    "turma 2B",
    "pix",
])

bot.resetar(); pedido.clear()

print(f"{Fore.CYAN}{'='*54}")
print("  Demonstracao concluida! Agora e sua vez.")
print(f"{'='*54}{Style.RESET_ALL}")


# ════════════════════════════════════════════════════════════
#  PONTO DE ENTRADA — F5 / ▶ abre o chat
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print()
    bot.chat()
