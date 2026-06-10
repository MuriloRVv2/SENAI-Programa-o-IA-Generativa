# ╔══════════════════════════════════════════════════════════╗
# ║  📋  Bot Notas e Faltas Completo                   ║
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
# O que este bot faz:
#    Calcula media, nota necessaria para passar, porcentagem de faltas
#    e simula o resultado de uma prova de recuperacao.
# 
#    Diferenca do Grupo 1:
#    O Grupo 1 tinha 2 calculos. Este tem 4 calculos diferentes,
#    incluindo simulacao de recuperacao e alertas detalhados de faltas.
# 
#    Dica para estudo:
#    Este bot pode virar uma ferramenta real para voce!
#    Adapte os limites (media 7.0, max 25% de faltas) para as regras
#    da sua escola e use para calcular sua propria situacao.
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
#  2. Digite: python g2_ex07_notas_faltas.py
#  3. Pronto!
#
#  INSTALACAO (so na primeira vez — no terminal do projeto):
#    pip install pip install colorama scikit-learn
#
#  DURANTE O CHAT:
#    sair  → encerra o chat
#    reset → comeca uma nova conversa
# ════════════════════════════════════════════════════════════

import re, math, random
from colorama import Fore, Style, init; init(autoreset=True)

import re
import math
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
#  CODIGO DO EXEMPLO: Bot Notas e Faltas Completo
# ════════════════════════════════════════════════════════════

def calcular_media(msg, dados, ctx):
    notas=[float(n.replace(",",".")) for n in re.findall(r"\d+[.,]?\d*",msg)
           if 0<=float(n.replace(",","."))<=10]
    if len(notas)<2: return "Me manda pelo menos 2 notas! Ex: 'notas 7 8 e 6.5'"
    m=sum(notas)/len(notas)
    sit=("✅ APROVADO" if m>=7 else "⚠️ RECUPERACAO" if m>=5 else "❌ REPROVADO")
    return f"Notas: {notas}\nMedia: {m:.2f} | {sit}"

def nota_nec(msg, dados, ctx):
    notas=[float(n.replace(",",".")) for n in re.findall(r"\d+[.,]?\d*",msg)
           if 0<=float(n.replace(",","."))<=10]
    if not notas: return "Me manda as notas que voce ja tem!"
    rest=4-len(notas)
    if rest<=0: return f"Ja fez todas. Media: {sum(notas)/len(notas):.2f}"
    nec=max(0,min(10,(7*4-sum(notas))/rest))
    return (f"Notas: {notas} | Media parcial: {sum(notas)/len(notas):.2f}\n"
            f"Precisa de {nec:.1f}/prova nas proximas {rest} provas")

def calc_faltas(msg, dados, ctx):
    nums=re.findall(r"\d+",msg)
    if not nums: return "Me diz: 'tenho X faltas em Y aulas'"
    f=int(nums[0]); t=int(nums[1]) if len(nums)>=2 else 80
    pct=f/t*100; mf=t*0.25; rest=max(0,mf-f)
    sit=("✅ OK" if pct<=25 else f"⚠️ ATENCAO! Pode faltar mais {int(rest)}x" if pct<=30 else "❌ REPROVADO POR FALTAS")
    return f"Faltas: {f}/{t} ({pct:.1f}%) | Limite: {int(mf)} | {sit}"

def simulacao_rec(msg, dados, ctx):
    notas=[float(n.replace(",",".")) for n in re.findall(r"\d+[.,]?\d*",msg)
           if 0<=float(n.replace(",","."))<=10]
    if len(notas)<2: return "Me manda: media atual e nota da recuperacao!"
    mf=(notas[0]+notas[1])/2
    sit="✅ APROVADO apos recuperacao!" if mf>=7 else "❌ Nao foi suficiente."
    return f"Media: {notas[0]} | Recuperacao: {notas[1]} | Final: {mf:.2f} | {sit}"

bot = MiniDialogflowPro("NotasBot")
bot.treinar_intent("media",frases=["calcular media","qual minha media","notas sao","tirei"],
    respostas=["..."],acao=calcular_media)
bot.treinar_intent("necessaria",frases=["quanto preciso","o que preciso para passar",
    "nota necessaria","para passar"],respostas=["..."],acao=nota_nec)
bot.treinar_intent("faltas",frases=["quantas faltas","calcula faltas","tenho faltas",
    "limite de falta"],respostas=["..."],acao=calc_faltas)
bot.treinar_intent("recuperacao",frases=["recuperacao","simular recuperacao",
    "media recuperacao"],respostas=["..."],acao=simulacao_rec)
bot.treinar_intent("regras",frases=["media para passar","nota minima","regras"],
    respostas=["Media: 7.0 | Recuperacao: 5.0-6.9 | Faltas: max 25% das aulas"])

print(f"\n{Fore.YELLOW}=== TESTANDO CALCULOS ESCOLARES ==={Style.RESET_ALL}\n")
bot.simular(["notas foram 7 8 e 6","tenho 5 e 6 quanto preciso",
             "12 faltas em 80 aulas","media 5.5 recuperacao 8"])


# ════════════════════════════════════════════════════════════
#  PONTO DE ENTRADA
#  Ao rodar com F5 / ▶, testes aparecem e chat abre em seguida!
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print()
    bot.chat()
