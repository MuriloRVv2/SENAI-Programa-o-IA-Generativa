# ╔══════════════════════════════════════════════════════════╗
# ║  😂  Bot Contador de Piadas por Categoria          ║
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
#     Um bot especializado em piadas com 4 categorias: programacao, escola,
#     matematica e trocadilho. Sem repetir a mesma piada!
#  
#  Conceito ensinado — ENTIDADE de CATEGORIA + BANCO de DADOS:
#     O bot usa um dicionario Python como banco de piadas.
#     A Entidade detecta QUAL categoria o usuario quer.
#     O sistema de "ja contadas" garante que a piada nao se repete.
#  
#  Pense assim:
#     e como um comediante que tem um caderno dividido por tipo de piada.
#     Voce pede "conta uma sobre escola" e ele escolhe do caderno certo,
#     sem repetir o que ja contou naquela noite!
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
#  2. Digite: python g2_ex04_piadas.py
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

PIADAS = {
    "programacao": [
        "Por que o programador usa oculos escuros? Nao suporta Java! ☕",
        "Qual o animal favorito do programador? O bug! 🐛",
        "Por que programador nao tem amigos? Tem o StackOverflow! 🤓",
        "Como termina a historia do HTML? Fechando a tag! </fim>",
    ],
    "escola": [
        "Por que o estudante levou escada? Queria chegar ao ALTO da turma! 📚",
        "O que o zero disse pro oito? Que cinto bonito! 0️⃣",
        "Por que o livro de historia e chato? Vive no passado! 📖",
    ],
    "matematica": [
        "Por que o 6 tem medo do 7? Porque 7 comeu 9! (7,8,9) 😂",
        "Por que a geometria e dramatica? Tem MUITOS angulos! 📐",
        "O que e pi ao quadrado? Uma torta redonda! 🥧",
    ],
    "trocadilho": [
        "O que o peixe disse quando bateu na pedra? DROGA! 🐟",
        "Por que o sorvete nao foi ao cinema? Derreteu na fila! 🍦",
        "O que a lampada disse pra outra? Voce me ilumina! 💡",
    ],
}

# Rastreia quais piadas ja foram contadas (para nao repetir)
ja_contadas = set()

def contar_piada(msg, dados):
    cat = dados.get("categoria", "programacao").lower()
    if cat not in PIADAS:
        cat = "programacao"
    # Filtra as que ainda nao foram contadas
    disponiveis = [p for p in PIADAS[cat] if p not in ja_contadas]
    if not disponiveis:
        ja_contadas.clear()  # reseta quando acabar o repertorio
        disponiveis = PIADAS[cat]
    piada = random.choice(disponiveis)
    ja_contadas.add(piada)
    return (f"😂 [{cat.upper()}]\n\n{piada}\n\n"
            f"Diz 'mais uma' para ouvir outra!")

bot = MiniDialogflow("PiadaBot")

bot.treinar_intent(
    nome="pedir_piada",
    frases=["conta uma piada", "piada", "mais uma", "outra piada",
            "me faz rir", "piada de programacao", "piada de escola",
            "piada de matematica", "piada de trocadilho"],
    entidades=[{"nome": "categoria", "valores": list(PIADAS.keys())}],
    respostas=["Vai uma piada ai!"],
    acao=contar_piada
)

bot.treinar_intent(
    nome="categorias",
    frases=["quais categorias", "tipos de piada", "o que tem",
            "quais opcoes", "lista de categorias"],
    respostas=[f"Tenho piadas de: {', '.join(PIADAS.keys())}!\n"
               f"Diz 'piada de [categoria]' para ouvir!"]
)

bot.treinar_intent(
    nome="quantas_piadas",
    frases=["quantas piadas voce tem", "total de piadas", "repertorio"],
    respostas=[f"Tenho {sum(len(v) for v in PIADAS.values())} piadas no total! 🎭"]
)

# ════════════════════════════════════════════════════════════
#  TESTES AUTOMATICOS (rodam ao executar o arquivo)
# ════════════════════════════════════════════════════════════

print(f"\n{Fore.YELLOW}{'='*50}")
print("  TESTANDO O BOT DE PIADAS")
print(f"{'='*50}{Style.RESET_ALL}\n")

for msg in ["piada de programacao", "mais uma", "piada de escola",
            "quais categorias tem", "quantas piadas voce tem"]:
    r = bot.detectar(msg)
    print(f"  Voce: '{msg}'")
    print(f"  Bot : '{r['resposta'][:90]}'\n")

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
