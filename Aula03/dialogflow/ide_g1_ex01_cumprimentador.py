# ╔══════════════════════════════════════════════════════════╗
# ║  👋  Bot Cumprimentador                            ║
# ║  Nivel: Facil                                            ║
# ║  Ambiente: PyCharm / VSCode / Terminal                  ║
# ╚══════════════════════════════════════════════════════════╝
#
# ════════════════════════════════════════════════════════════
#  OLA, ALUNO! 👋  LEIA ANTES DE RODAR
# ════════════════════════════════════════════════════════════
#
# ════════════════════════════════════════════════════════════
#
#  O que este bot faz:
#     Este e o bot mais simples que existe — ele aprende a dizer oi, tchau
#     e obrigado. Parece pouco, mas e o ponto de partida de QUALQUER chatbot
#     profissional! Ate a Siri e a Alexa comecaram assim.
#  
#  Conceito ensinado — INTENT:
#     Intent e a INTENCAO do usuario. Quando alguem digita "oi" ou "bom dia",
#     a intencao e a mesma: saudar. O bot aprende a reconhecer essa intencao
#     mesmo com palavras diferentes!
#  
#  Pense assim:
#     e como ensinar um filhote de cachorro: voce mostra exemplos ("senta!",
#     "senta!", "senta!") e ele aprende. Aqui voce mostra frases de exemplo
#     e o bot aprende o que cada tipo de mensagem representa.
#  
#  Como usar apos rodar:
#     bot.chat()            → abre o chat interativo
#     bot.detectar("oi")   → retorna o resultado sem abrir o chat
#     bot.resetar()         → limpa o contexto e comeca de novo
#
#
# ────────────────────────────────────────────────────────────
#  COMO RODAR NO PYCHARM:
#  1. Abra este arquivo no PyCharm
#  2. Clique no botao verde ▶ (ou pressione Shift+F10)
#  3. Os testes aparecem no terminal e o chat abre em seguida!
#
#  COMO RODAR NO VSCODE:
#  1. Abra este arquivo no VSCode
#  2. Pressione F5  OU  clique em ▶ Run Python File
#  3. Interaja com o bot no terminal integrado
#
#  COMO RODAR NO TERMINAL:
#  1. Abra o terminal na pasta do projeto
#  2. Digite: python g1_ex01_cumprimentador.py
#  3. Pronto!
#
#  INSTALACAO (so na primeira vez — no terminal do projeto):
#    pip install pip install colorama
#
#  DURANTE O CHAT:
#    sair  → encerra o chat
#    reset → comeca uma nova conversa
# ════════════════════════════════════════════════════════════

import re
import random
from colorama import Fore, Style, init
init(autoreset=True)


import re
import random
from colorama import Fore, Style, init
init(autoreset=True)


import re
import random
from colorama import Fore, Style, init
init(autoreset=True)


class MiniDialogflow:
    """
    Simula o Dialogflow ES por dentro — versao com context-aware fallback.
    Quando ha contexto ativo e a mensagem nao atinge o limiar minimo,
    o bot roteia para o intent daquele contexto em vez de cair no fallback.
    Isso garante que respostas livres (quiz, agendamento, etc.) funcionem!
    """

    def __init__(self, nome: str):
        self.nome     = nome
        self.intents  = {}
        self.contexto = None
        self.dados    = {}

    def treinar_intent(self, nome, frases, respostas,
                       entidades=None, exige_ctx=None,
                       gera_ctx=None, acao=None):
        """
        Cadastra um intent — equivale a criar um Intent no Dialogflow.
        nome      : identificador  (ex: "saudacao")
        frases    : Training Phrases  (ex: ["oi", "ola", "hey"])
        respostas : respostas possiveis (escolhida aleatoriamente)
        entidades : [{"nome":"sabor", "valores":["calabresa"]}]
        exige_ctx : so ativa se contexto == este valor
        gera_ctx  : muda o contexto ao ser ativado
        acao      : funcao chamada ao ativar (Fulfillment/Webhook)
        """
        self.intents[nome] = {
            "frases"   : [f.lower().strip() for f in frases],
            "respostas": respostas,
            "entidades": entidades or [],
            "exige_ctx": exige_ctx,
            "gera_ctx" : gera_ctx,
            "acao"     : acao,
        }

    def detectar(self, msg: str) -> dict:
        """
        Detecta o intent e retorna a resposta.
        Usa matching de palavras + context-aware fallback.
        """
        ml = msg.lower().strip()
        melhor, score = None, 0.0

        for nome, intent in self.intents.items():
            if intent["exige_ctx"] and self.contexto != intent["exige_ctx"]:
                continue
            for frase in intent["frases"]:
                pf = set(frase.split())
                pm = set(ml.split())
                s  = len(pm & pf) / len(pm | pf) if (pm | pf) else 0
                if frase in ml:
                    s = max(s, 0.85)
                if s > score:
                    score, melhor = s, nome

        LIMIAR = 0.18

        if not (melhor and score >= LIMIAR):
            # context-aware fallback: se ha contexto, usa o intent dele
            if self.contexto:
                candidatos = [(n, i) for n, i in self.intents.items()
                              if i["exige_ctx"] == self.contexto]
                if candidatos:
                    melhor = max(
                        candidatos,
                        key=lambda x: max(
                            (len(set(ml.split()) & set(f.split())) /
                             max(len(set(ml.split()) | set(f.split())), 1)
                             for f in x[1]["frases"]),
                            default=0
                        )
                    )[0]
                    score = 0.01
                else:
                    melhor = None
            else:
                melhor = None

        if melhor:
            intent = self.intents[melhor]
            if intent["gera_ctx"] is not None:
                self.contexto = intent["gera_ctx"]
            ents = self._extrair(ml, intent["entidades"])
            self.dados.update(ents)
            resp = random.choice(intent["respostas"])
            for k, v in {**self.dados, **ents}.items():
                resp = resp.replace(f"{{{k}}}", str(v))
            if intent["acao"]:
                r2 = intent["acao"](ml, self.dados)
                if r2:
                    resp = r2
        else:
            melhor, score, ents = "fallback", 0.0, {}
            resp = random.choice([
                "Nao entendi. Pode reformular?",
                "Hmm, tenta de outro jeito?",
                "Nao captei! Me explica diferente?",
            ])

        return {
            "intent"   : melhor,
            "score"    : round(score, 2),
            "resposta" : resp,
            "entidades": ents if melhor != "fallback" else {},
            "contexto" : self.contexto,
        }

    def _extrair(self, msg: str, defs: list) -> dict:
        r = {}
        for d in defs:
            for v in d.get("valores", []):
                if v.lower() in msg:
                    r[d["nome"]] = v
                    break
            if d.get("regex") and d["nome"] not in r:
                m = re.search(d["regex"], msg, re.IGNORECASE)
                if m:
                    r[d["nome"]] = m.group()
        return r

    def resetar(self):
        """Limpa contexto e dados — nova sessao."""
        self.contexto = None
        self.dados    = {}

    def chat(self, debug: bool = True):
        """
        Chat interativo. Funciona no terminal, PyCharm e VSCode.
        Digite suas mensagens e pressione Enter.
        Comandos especiais:
          sair  -> encerra o chat
          reset -> nova conversa (limpa contexto)
        """
        print(f"\n{Fore.CYAN}{'='*54}")
        print(f"  Chatbot: {self.nome}")
        print(f"  'sair' = encerrar | 'reset' = nova conversa")
        print(f"{'='*54}{Style.RESET_ALL}\n")

        while True:
            try:
                user_input = input(f"{Fore.GREEN}Voce >>> {Style.RESET_ALL}").strip()
            except (EOFError, KeyboardInterrupt):
                print(f"\n{Fore.CYAN}  Ate mais!{Style.RESET_ALL}")
                break

            if not user_input:
                continue
            if user_input.lower() == "sair":
                print(f"\n{Fore.CYAN}  Ate mais! 👋{Style.RESET_ALL}")
                break
            if user_input.lower() == "reset":
                self.resetar()
                print(f"{Fore.YELLOW}  [Nova conversa — contexto limpo]{Style.RESET_ALL}\n")
                continue

            resultado = self.detectar(user_input)
            print(f"{Fore.BLUE}Bot  >>> {resultado['resposta']}{Style.RESET_ALL}")
            if debug:
                ctx_str = resultado["contexto"] or "nenhum"
                print(f"{Fore.WHITE}         "
                      f"[intent: {resultado['intent']} | "
                      f"certeza: {resultado['score']:.0%} | "
                      f"contexto: {ctx_str}]{Style.RESET_ALL}")
            print()


# ════════════════════════════════════════════════════════════
#  CONFIGURACAO DO BOT
#  (escopo global — o 'bot' fica disponivel em qualquer celula!)
# ════════════════════════════════════════════════════════════

# ──────────────────────────────────────────────────────────────
# CONFIGURACAO DO BOT (escopo global — acessivel de qualquer celula!)
# ──────────────────────────────────────────────────────────────

bot = MiniDialogflow("CumprimentaBot")

# INTENT: saudacao
# frases = exemplos de como o usuario pode dizer "oi"
# respostas = o bot escolhe uma aleatoriamente a cada vez
bot.treinar_intent(
    nome="saudacao",
    frases=["oi", "ola", "hey", "bom dia", "boa tarde",
            "boa noite", "eai", "salve", "opa", "oi tudo bem"],
    respostas=[
        "Oi! Tudo certo por aqui 😊",
        "Ola! Pronto pra conversar!",
        "Hey! Como posso ajudar?",
        "Bom dia! (ou tarde, ou noite — nunca sei hehe)",
    ]
)

# INTENT: despedida
bot.treinar_intent(
    nome="despedida",
    frases=["tchau", "ate mais", "ate logo", "flw", "falou",
            "xau", "bye", "tenho que ir", "vou sair", "ate amanha"],
    respostas=[
        "Tchau! Foi bom conversar! 👋",
        "Ate mais! Volte quando quiser!",
        "Flw! Cuida-se!",
    ]
)

# INTENT: agradecimento
bot.treinar_intent(
    nome="agradecimento",
    frases=["obrigado", "valeu", "thanks", "obg",
            "muito obrigado", "obrigada", "grato"],
    respostas=[
        "De nada! Sempre que precisar 😄",
        "Por nada! Isso e pra isso que estou aqui!",
        "Disponha!",
    ]
)

# INTENT: quem e o bot
bot.treinar_intent(
    nome="quem_es",
    frases=["quem e voce", "o que voce faz", "voce e um robo",
            "como voce se chama", "qual seu nome"],
    respostas=[
        "Sou o CumprimentaBot! Feito em Python puro! 🤖",
        "Sou um chatbot criado nesta aula. Aprendi a conversar hoje!",
    ]
)

# ════════════════════════════════════════════════════════════
#  TESTES AUTOMATICOS (rodam ao executar o arquivo)
# ════════════════════════════════════════════════════════════

# ──────────────────────────────────────────────────────────────
# TESTES AUTOMATICOS (rodam ao executar o arquivo)
# ──────────────────────────────────────────────────────────────
print(f"\n{Fore.YELLOW}{'='*50}")
print("  TESTES AUTOMATICOS")
print(f"{'='*50}{Style.RESET_ALL}\n")

testes = [
    ("oi tudo bem",              "saudacao"),
    ("muito obrigado pela ajuda","agradecimento"),
    ("flw ate amanha",           "despedida"),
    ("quem e voce",              "quem_es"),
    ("isso nao faz sentido",     "fallback"),
]
certos = 0
for msg, esperado in testes:
    r = bot.detectar(msg)
    ok = r["intent"] == esperado
    certos += int(ok)
    emoji = "✓" if ok else "✗"
    print(f"  {Fore.GREEN if ok else Fore.RED}{emoji}{Style.RESET_ALL} Voce: '{msg}'")
    print(f"     Bot: '{r['resposta']}' [{r['intent']}]\n")

print(f"  Placar: {certos}/{len(testes)} corretos\n")
print(f"{Fore.CYAN}{'='*50}")
print(f"{'='*50}{Style.RESET_ALL}")

# ════════════════════════════════════════════════════════════
#  PONTO DE ENTRADA
#  Ao rodar com F5 / botao ▶, os testes aparecem e o chat
#  abre automaticamente em seguida!
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Os testes acima ja rodaram.
    # Agora abre o chat interativo direto no terminal!
    print()
    bot.chat()
