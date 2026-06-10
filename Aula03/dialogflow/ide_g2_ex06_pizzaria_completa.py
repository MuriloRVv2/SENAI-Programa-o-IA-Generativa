# ╔══════════════════════════════════════════════════════════╗
# ║  🍕  Bot Pizzaria Completa                         ║
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
#    Versao completa da pizzaria com 5 etapas: sabor, tamanho, borda
#    recheada, tipo de entrega (delivery ou retirada) e endereco/nome.
#    Calcula o preco final automaticamente!
# 
#    Diferenca do Grupo 1:
#    O bot basico tinha 3 etapas. Este tem 5 etapas, borda recheada,
#    opcao de retirada no balcao e calculo do preco total!
# 
#    Conceito ensinado: PRECIFICACAO no FULFILLMENT
#    O Fulfillment pode fazer qualquer calculo — buscar preco num banco
#    de dados, aplicar desconto, calcular frete. Aqui, calculamos o
#    total do pedido somando pizza + borda + entrega.
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
#  2. Digite: python g2_ex06_pizzaria_completa.py
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
#  CODIGO DO EXEMPLO: Bot Pizzaria Completa
# ════════════════════════════════════════════════════════════

PRECOS = {"p":25.0,"m":35.0,"g":45.0,"gg":55.0}
BORDAS = {"normal":0,"catupiry":8.0,"cheddar":8.0,"chocolate":10.0}
SABORES= ["calabresa","frango","quatro queijos","margherita","portuguesa","pepperoni"]
TAMANHOS={"p":"Pequena","m":"Media","g":"Grande","gg":"GG"}
pedido = {}

def salvar_sabor(msg, dados, ctx):
    for s in SABORES:
        if s in msg:
            pedido["sabor"]=s.title(); pedido["preco"]=0
            return f"Pizza de {s.title()}!\nQual tamanho? P(R$25)|M(R$35)|G(R$45)|GG(R$55)"
    return f"Sabores: {', '.join(SABORES[:4])}..."

def salvar_tamanho(msg, dados, ctx):
    for sig,nome in TAMANHOS.items():
        if f" {sig} " in f" {msg} " or msg.strip()==sig:
            pedido["tamanho"]=nome; pedido["preco"]=PRECOS[sig]
            return f"Tamanho {nome}!\nBorda: Normal(gratis)|Catupiry(+R$8)|Cheddar(+R$8)|Chocolate(+R$10)"
    return "Escolha: P, M, G ou GG"

def salvar_borda(msg, dados, ctx):
    for b,v in BORDAS.items():
        if b in msg: pedido["borda"]=b.title(); pedido["preco"]+=v; break
    else: pedido["borda"]="Normal"
    return f"Borda {pedido['borda']}!\nEntrega(+R$5) ou Retirada(gratis)?"

def salvar_entrega(msg, dados, ctx):
    if any(p in msg for p in ["entrega","delivery","minha casa"]):
        pedido["entrega"]="Entrega"; pedido["preco"]+=5.0
        return f"Entrega! Total: R${pedido['preco']:.2f}\nQual o endereco?"
    pedido["entrega"]="Retirada"
    return f"Retirada no balcao! Total: R${pedido['preco']:.2f}\nNome para retirada?"

def finalizar(msg, dados, ctx):
    cod=f"PED-{random.randint(10000,99999)}"
    return (f"PEDIDO {cod} CONFIRMADO!\n"
            f"Pizza: {pedido.get('sabor')} {pedido.get('tamanho')}\n"
            f"Borda: {pedido.get('borda')} | {pedido.get('entrega')}\n"
            f"Total: R${pedido.get('preco',0):.2f} | Previsao: 40min")

bot = MiniDialogflowPro("PizzaBot")
bot.treinar_intent("iniciar",frases=["quero pizza","pedir pizza","fazer pedido","pizza"],
    respostas=[f"Qual sabor? {', '.join(SABORES[:4])} e mais!"],gera_ctx="sabor")
bot.treinar_intent("sabor",frases=SABORES+["quero a de"],
    respostas=["..."],exige_ctx="sabor",gera_ctx="tamanho",acao=salvar_sabor)
bot.treinar_intent("tamanho",frases=["p","m","g","gg","pequena","media","grande"],
    respostas=["..."],exige_ctx="tamanho",gera_ctx="borda",acao=salvar_tamanho)
bot.treinar_intent("borda",frases=["normal","catupiry","cheddar","chocolate","sem borda"],
    respostas=["..."],exige_ctx="borda",gera_ctx="entrega",acao=salvar_borda)
bot.treinar_intent("entrega",frases=["entrega","delivery","retirada","buscar","vou la"],
    respostas=["..."],exige_ctx="entrega",gera_ctx="local",acao=salvar_entrega)
bot.treinar_intent("local",frases=["rua","av","meu nome e","nome","bairro"],
    respostas=["..."],exige_ctx="local",acao=finalizar)

print(f"\n{Fore.YELLOW}=== PEDIDO COMPLETO ==={Style.RESET_ALL}\n")
bot.simular(["quero pedir pizza","calabresa","G","cheddar","entrega","rua das flores 50"])


# ════════════════════════════════════════════════════════════
#  PONTO DE ENTRADA
#  Ao rodar com F5 / ▶, testes aparecem e chat abre em seguida!
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print()
    bot.chat()
