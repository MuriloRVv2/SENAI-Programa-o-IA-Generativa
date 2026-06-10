# ╔══════════════════════════════════════════════════════════╗
# ║  🏆  Bot Quiz Turbo com Ranking                    ║
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
#    Quiz com 4 categorias (programacao, matematica, geral, tecnologia),
#    5 perguntas por rodada e um ranking persistente por jogador.
# 
#    Diferenca do Grupo 1:
#    O Grupo 1 tinha 3 perguntas fixas. Este tem 20 perguntas embaralhadas,
#    4 categorias escolhidas pelo usuario e um ranking que salva recordes!
# 
#    Conceito ensinado: DADOS PERSISTENTES na SESSAO
#    O ranking continua entre multiplas partidas. Isso simula o que
#    acontece em sistemas reais com bancos de dados.
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
#  2. Digite: python g2_ex08_quiz_turbo.py
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
#  CODIGO DO EXEMPLO: Bot Quiz Turbo com Ranking
# ════════════════════════════════════════════════════════════

BANCO = {
    "programacao":[
        {"p":"O que significa CPU?","r":"central processing unit","alt":["central","processador"]},
        {"p":"Linguagem criada pelo Google?","r":"go","alt":["golang"]},
        {"p":"O que e HTML?","r":"hypertext markup language","alt":["hyper text"]},
        {"p":"Pai da computacao?","r":"alan turing","alt":["turing","alan"]},
        {"p":"Para que serve o pip?","r":"instalar pacotes","alt":["instalar","pacotes python"]},
    ],
    "matematica":[
        {"p":"Quanto e 15% de 200?","r":"30","alt":["trinta"]},
        {"p":"Raiz quadrada de 144?","r":"12","alt":["doze"]},
        {"p":"PI com 2 casas decimais?","r":"3.14","alt":["3,14"]},
        {"p":"Quanto e 2 elevado a 8?","r":"256","alt":[]},
        {"p":"Qual menor numero primo?","r":"2","alt":["dois"]},
    ],
}
BANCO["geral"]=[
    {"p":"Capital do Brasil?","r":"brasilia","alt":["a capital"]},
    {"p":"Planeta mais proximo do Sol?","r":"mercurio","alt":["mercúrio"]},
    {"p":"Quem pintou a Mona Lisa?","r":"da vinci","alt":["leonardo","leonardo da vinci"]},
    {"p":"Qual maior oceano?","r":"pacifico","alt":["oceano pacifico"]},
    {"p":"Em que ano acabou a 2a Guerra?","r":"1945","alt":["noventa e cinco"]},
]
BANCO["tecnologia"]=[
    {"p":"Ano de criacao do Python?","r":"1991","alt":["noventa e um"]},
    {"p":"O que e uma API?","r":"interface de programacao","alt":["application programming"]},
    {"p":"O que e IA generativa?","r":"cria conteudo","alt":["gera conteudo","generativa"]},
    {"p":"Fundador da Microsoft?","r":"bill gates","alt":["gates","william"]},
    {"p":"O que e Machine Learning?","r":"aprendizado de maquina","alt":["aprende com dados"]},
]
ranking={}; estado={"rodando":False,"questoes":[],"idx":0,"pontos":0,"jogador":"?","cat":"geral"}

def iniciar(msg,dados,ctx):
    cat="geral"
    for c in BANCO:
        if c in msg: cat=c; break
    nome_m=re.search(r"me chamo ([a-z]+)|sou ([a-z]+)",msg,re.IGNORECASE)
    nome=((nome_m.group(1) or nome_m.group(2)).title() if nome_m else "Jogador")
    qs=BANCO[cat].copy(); random.shuffle(qs)
    estado.update({"rodando":True,"questoes":qs[:5],"idx":0,"pontos":0,"jogador":nome,"cat":cat})
    return f"Quiz {cat.upper()}, {nome}!\nPergunta 1/5:\n{qs[0]['p']}"

def responder(msg,dados,ctx):
    if not estado["rodando"]: return "Use 'quero jogar' para comecar!"
    q=estado["questoes"][estado["idx"]]
    ok=q["r"] in msg.lower() or any(a in msg.lower() for a in q.get("alt",[]))
    if ok: estado["pontos"]+=1; fb="✅ CORRETO!"
    else: fb=f"❌ Errado! Era: {q['r']}"
    estado["idx"]+=1
    if estado["idx"]<len(estado["questoes"]):
        prox=estado["questoes"][estado["idx"]]
        return f"{fb}\nPergunta {estado['idx']+1}/5:\n{prox['p']}"
    pts=estado["pontos"]; nome=estado["jogador"]
    ranking[nome]=max(ranking.get(nome,0),pts)
    estado["rodando"]=False
    nota="🏆 Perfeito!" if pts==5 else "🥇 Excelente!" if pts>=4 else "👍 Bom!" if pts>=3 else "📚 Estude mais!"
    return f"{fb}\nFIM! {nome}: {pts}/5 {nota}"

bot=MiniDialogflowPro("QuizBot")
bot.treinar_intent("iniciar",frases=["quero jogar","quiz","bora","comecar","jogar",
    "quiz de programacao","quiz de matematica"],respostas=["Iniciando!"],
    gera_ctx="quiz",acao=iniciar)
bot.treinar_intent("resposta",frases=["central","html","go","brasilia","1945","1991",
    "30","12","minha resposta"],respostas=["..."],exige_ctx="quiz",acao=responder)
bot.treinar_intent("ranking",frases=["ranking","placar","pontuacao","leaderboard"],
    respostas=["..."],acao=lambda m,d,c: ("Ranking:\n"+
        "\n".join(f"  {n}: {p}" for n,p in sorted(ranking.items(),key=lambda x:-x[1]))
        or "  Nenhum jogador ainda!"))

print(f"\n{Fore.YELLOW}=== SIMULANDO QUIZ DE PROGRAMACAO ==={Style.RESET_ALL}\n")
bot.simular(["quero jogar quiz de programacao","central processing unit",
             "go","hypertext markup language","alan turing","instalar pacotes","ranking"])


# ════════════════════════════════════════════════════════════
#  PONTO DE ENTRADA — F5 / ▶ abre testes + chat automaticamente
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print()
    bot.chat()
