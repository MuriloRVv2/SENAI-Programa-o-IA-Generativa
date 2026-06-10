# ╔══════════════════════════════════════════════════════════╗
# ║  🧠  Bot Quiz de Programacao                       ║
# ║  Nivel: Intermediario                                    ║
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
#     Um quiz com 3 perguntas de programacao! O bot rastreia a pontuacao
#     durante a conversa e da um feedback final com classificacao.
#  
#  Conceito ensinado — ESTADO entre turnos:
#     Em conversas longas, o bot precisa lembrar informacoes entre mensagens:
#     quantos pontos o usuario tem, em qual pergunta esta, etc.
#     Aqui isso e feito com um dicionario Python que persiste na sessao.
#  
#  Pense assim:
#     e como um jogo de tabuleiro. O tabuleiro (estado) lembra onde cada
#     jogador esta e quantos pontos tem. O bot e o narrador do jogo!
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
#  2. Digite: python g1_ex06_quiz.py
#  3. Pronto!
#
#  INSTALACAO (so na primeira vez — no terminal do projeto):
#    pip install pip install colorama scikit-learn
#
#  DURANTE O CHAT:
#    sair  → encerra o chat
#    reset → comeca uma nova conversa
# ════════════════════════════════════════════════════════════

import re
import math
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


import re
import math
import random
from colorama import Fore, Style, init
init(autoreset=True)


class MiniDialogflowPro:
    """
    Dialogflow aprimorado com TF-IDF + context-aware fallback.
    TF-IDF: palavras raras pesam mais que palavras comuns.
    Context-aware fallback: nunca cai no fallback se ha contexto ativo.
    """

    def __init__(self, nome: str):
        self.nome     = nome
        self.intents  = {}
        self.contexto = None
        self.dados    = {}
        self._idf     = {}

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

    def _tok(self, t: str) -> list:
        return re.findall(r"[a-z0-9]+", t.lower())

    def _recalcular_idf(self):
        docs = [set(self._tok(f))
                for intent in self.intents.values()
                for f in intent["frases"]]
        if not docs:
            return
        N = len(docs)
        freq = {}
        for d in docs:
            for p in d:
                freq[p] = freq.get(p, 0) + 1
        self._idf = {p: math.log(N / (c + 1)) for p, c in freq.items()}

    def _tfidf(self, t: str) -> dict:
        toks = self._tok(t)
        tf   = {}
        for tk in toks:
            tf[tk] = tf.get(tk, 0) + 1 / max(len(toks), 1)
        return {tk: v * self._idf.get(tk, 0) for tk, v in tf.items()}

    def _cosseno(self, v1: dict, v2: dict) -> float:
        w   = set(v1) | set(v2)
        dot = sum(v1.get(p, 0) * v2.get(p, 0) for p in w)
        m1  = math.sqrt(sum(x**2 for x in v1.values()))
        m2  = math.sqrt(sum(x**2 for x in v2.values()))
        return dot / (m1 * m2) if m1 and m2 else 0.0

    def _score_intent(self, v_msg: dict, frases: list) -> float:
        return max((self._cosseno(v_msg, self._tfidf(f)) for f in frases),
                   default=0.0)

    def detectar(self, msg: str) -> dict:
        """
        Detecta o intent com TF-IDF + context-aware fallback.
        """
        ml    = msg.lower().strip()
        v_msg = self._tfidf(ml)
        melhor, score = None, 0.0

        for nome, intent in self.intents.items():
            if intent["exige_ctx"] and self.contexto != intent["exige_ctx"]:
                continue
            s = self._score_intent(v_msg, intent["frases"])
            if s > score:
                score, melhor = s, nome

        LIMIAR = 0.12

        if not (melhor and score >= LIMIAR):
            # context-aware fallback
            if self.contexto:
                candidatos = [(n, i) for n, i in self.intents.items()
                              if i["exige_ctx"] == self.contexto]
                if candidatos:
                    melhor = max(
                        candidatos,
                        key=lambda x: self._score_intent(v_msg, x[1]["frases"])
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
                r2 = intent["acao"](ml, self.dados, {})
                if r2:
                    resp = r2
        else:
            melhor, score, ents = "fallback", 0.0, {}
            resp = random.choice([
                "Hmm, nao entendi. Pode reformular?",
                "Tenta de outro jeito?",
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
        """Reinicia contexto e dados."""
        self.contexto = None
        self.dados    = {}

    def chat(self, debug: bool = True):
        """
        Chat interativo. Funciona no terminal, PyCharm e VSCode.
        'sair' = encerrar | 'reset' = nova conversa
        """
        print(f"\n{Fore.CYAN}{'='*54}")
        print(f"  Chatbot Pro: {self.nome}")
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
                print(f"{Fore.YELLOW}  [Nova conversa]{Style.RESET_ALL}\n")
                continue
            r = self.detectar(user_input)
            print(f"{Fore.BLUE}Bot  >>> {r['resposta']}{Style.RESET_ALL}")
            if debug:
                ctx_str = r["contexto"] or "nenhum"
                print(f"{Fore.WHITE}         "
                      f"[intent: {r['intent']} | "
                      f"certeza: {r['score']:.0%} | "
                      f"contexto: {ctx_str}]{Style.RESET_ALL}")
            print()

    def simular(self, mensagens: list):
        """Roda mensagens automaticamente — para demonstracoes."""
        for msg in mensagens:
            r = self.detectar(msg)
            print(f"  Voce: {Fore.GREEN}{msg}{Style.RESET_ALL}")
            print(f"  Bot : {Fore.BLUE}{r['resposta']}{Style.RESET_ALL}\n")


# ════════════════════════════════════════════════════════════
#  CONFIGURACAO DO BOT
#  (escopo global — o 'bot' fica disponivel em qualquer celula!)
# ════════════════════════════════════════════════════════════

PERGUNTAS = [
    {
        "pergunta" : "O que significa CPU?",
        "resposta" : "central processing unit",
        "aceitar"  : ["central", "processador", "unidade central"],
    },
    {
        "pergunta" : "O que e HTML?",
        "resposta" : "hypertext markup language",
        "aceitar"  : ["hyper text", "html", "linguagem de marcacao"],
    },
    {
        "pergunta" : "Para que serve o Python?",
        "resposta" : "programacao geral",
        "aceitar"  : ["programar", "automatizar", "ia", "data science", "scripts"],
    },
]

# Estado do quiz (dicionario global)
estado = {"rodando": False, "idx": 0, "pontos": 0}

def iniciar_quiz(msg, dados, ctx):
    estado.update({"rodando": True, "idx": 0, "pontos": 0})
    p = PERGUNTAS[0]
    return (f"Quiz iniciado! {len(PERGUNTAS)} perguntas.\n\n"
            f"Pergunta 1/{len(PERGUNTAS)}:\n{p['pergunta']}")

def verificar_resposta(msg, dados, ctx):
    if not estado["rodando"]:
        return "Diz 'quero jogar' para comecar!"
    idx = estado["idx"]
    q   = PERGUNTAS[idx]
    acertou = (q["resposta"] in msg.lower() or
               any(a in msg.lower() for a in q["aceitar"]))
    if acertou:
        estado["pontos"] += 1
        feedback = "CORRETO! ✅"
    else:
        feedback = f"Errado! ❌ Era: {q['resposta']}"
    estado["idx"] += 1
    if estado["idx"] < len(PERGUNTAS):
        prox = PERGUNTAS[estado["idx"]]
        return (f"{feedback}\n\n"
                f"Pergunta {estado['idx']+1}/{len(PERGUNTAS)}:\n{prox['pergunta']}")
    pts = estado["pontos"]
    estado["rodando"] = False
    nota = ("🏆 Perfeito!" if pts == 3
            else "🥇 Muito bom!" if pts == 2
            else "📚 Estude mais!")
    return (f"{feedback}\n\n"
            f"FIM DO QUIZ! Voce fez {pts}/{len(PERGUNTAS)}!\n{nota}\n\n"
            f"Diz 'quero jogar' para uma nova rodada!")

bot = MiniDialogflowPro("QuizBot")

bot.treinar_intent(
    nome="iniciar",
    frases=["quero jogar", "comecar quiz", "bora", "quiz", "jogar"],
    respostas=["Iniciando quiz!"],
    gera_ctx="quiz_ativo",
    acao=iniciar_quiz
)

bot.treinar_intent(
    nome="resposta_quiz",
    frases=[
        # respostas especificas das perguntas
        "central processing unit", "processador", "unidade central",
        "hypertext markup language", "linguagem de marcacao", "html",
        "programacao geral", "automatizar", "scripts", "ia", "data science",
        # frases genericas de resposta
        "minha resposta e", "acho que e", "e o", "e a", "resposta",
        "seria", "minha resposta seria", "eu diria que",
    ],
    respostas=["Verificando..."],
    exige_ctx="quiz_ativo",
    acao=verificar_resposta
)

# ════════════════════════════════════════════════════════════
#  TESTES AUTOMATICOS (rodam ao executar o arquivo)
# ════════════════════════════════════════════════════════════

print(f"\n{Fore.YELLOW}{'='*50}")
print("  SIMULANDO QUIZ COMPLETO")
print(f"{'='*50}{Style.RESET_ALL}\n")

bot.simular([
    "quero jogar",
    "central processing unit",
    "hypertext markup language",
    "programacao geral",
])

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
