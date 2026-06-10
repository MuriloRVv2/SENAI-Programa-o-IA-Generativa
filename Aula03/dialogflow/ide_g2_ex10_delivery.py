# ╔══════════════════════════════════════════════════════════╗
# ║  🛵  Bot de Delivery Completo                      ║
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
#    Sistema completo de delivery com cardapio, carrinho de compras,
#    cupom de desconto, calculo de frete e confirmacao do pedido.
# 
#    Conceito ensinado: CARRINHO DE COMPRAS no BOT
#    O carrinho persiste durante a conversa, aceita multiplos itens
#    e aplica descontos com codigo de cupom. E um fluxo real de e-commerce
#    implementado como chatbot!
# 
#    Pense assim:
#    e como o iFood so que por mensagem de texto.
#    Voce vai pedindo itens, o bot vai adicionando no carrinho,
#    e no final confirma o pedido com o total calculado.
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
#  2. Digite: python g2_ex10_delivery.py
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
#  CODIGO DO EXEMPLO: Bot de Delivery Completo
# ════════════════════════════════════════════════════════════

CARDAPIO={"x-burguer":22.90,"x-bacon":27.90,"x-tudo":32.90,"frango":24.90,
          "salada":19.90,"batata":12.90,"refrigerante":7.90,"suco":9.90,"sorvete":11.90}
CUPONS={"DESC10":0.10,"FRETE0":0,"PROMO20":0.20}
FRETE=5.90; carrinho=[]; slots_pedido={}

def cardapio(msg,dados,ctx):
    linhas=["Cardapio:\n"]
    for item,preco in CARDAPIO.items():
        linhas.append(f"  {item.title():<20} R${preco:.2f}")
    return "\n".join(linhas)+"\n\nDiz o nome do item para adicionar!"

def adicionar(msg,dados,ctx):
    adicionados=[]
    for item,preco in CARDAPIO.items():
        if item in msg.lower():
            qtd_m=re.search(r"(\d+)\s*"+item,msg.lower())
            qtd=int(qtd_m.group(1)) if qtd_m else 1
            for _ in range(qtd): carrinho.append({"item":item,"preco":preco})
            adicionados.append(f"{qtd}x {item.title()}")
    if adicionados:
        total=sum(i["preco"] for i in carrinho)
        return (f"Adicionado: {', '.join(adicionados)}\n"
                f"Carrinho: {len(carrinho)} itens | R${total:.2f}\n"
                f"Continue ou diz 'fechar pedido'")
    return "Item nao encontrado! Diz 'cardapio' para ver as opcoes."

def ver_carrinho(msg,dados,ctx):
    if not carrinho: return "Carrinho vazio!"
    linhas=["Seu carrinho:\n"]
    for i,item in enumerate(carrinho,1):
        linhas.append(f"  {i}. {item['item'].title()} — R${item['preco']:.2f}")
    linhas.append(f"\nSubtotal: R${sum(i['preco'] for i in carrinho):.2f} (+frete R${FRETE:.2f})")
    return "\n".join(linhas)

def cupom(msg,dados,ctx):
    cs=[c for c in CUPONS if c in msg.upper()]
    if cs: slots_pedido["cupom"]=cs[0]; return f"Cupom '{cs[0]}' aplicado!"
    return f"Cupom invalido! Cupons: {', '.join(CUPONS.keys())}"

def fechar(msg,dados,ctx):
    if not carrinho: return "Carrinho vazio!"
    sub=sum(i["preco"] for i in carrinho)
    c=slots_pedido.get("cupom",""); desc=sub*CUPONS.get(c,0) if c and CUPONS.get(c,0)>0 else 0
    frete=0 if c=="FRETE0" else FRETE; total=sub-desc+frete
    slots_pedido["total"]=total
    return (f"Resumo:\n  Subtotal: R${sub:.2f}\n  Desconto: -R${desc:.2f}\n"
            f"  Frete: R${frete:.2f}\n  TOTAL: R${total:.2f}\n\nPagamento: Dinheiro|Cartao|PIX")

def pagar(msg,dados,ctx):
    metodo="pix" if "pix" in msg else "cartao" if "cart" in msg else "dinheiro"
    cod=f"DEL-{random.randint(10000,99999)}"; carrinho.clear()
    return (f"PEDIDO {cod} CONFIRMADO!\n"
            f"Pagamento: {metodo.upper()} | Total: R${slots_pedido.get('total',0):.2f}\n"
            f"Previsao: 35-45 minutos!")

bot=MiniDialogflowPro("DeliveryBot")
bot.treinar_intent("ver_card",frases=["cardapio","menu","o que tem","ver opcoes"],
    respostas=["..."],acao=cardapio)
bot.treinar_intent("add",frases=list(CARDAPIO.keys())+["quero","adicionar","pedir"],
    respostas=["..."],acao=adicionar)
bot.treinar_intent("carrinho",frases=["ver carrinho","meu pedido","quanto ta","total"],
    respostas=["..."],acao=ver_carrinho)
bot.treinar_intent("cupom_d",frases=["tenho cupom","desc10","frete0","promo20"],
    respostas=["..."],acao=cupom)
bot.treinar_intent("fechar_d",frases=["fechar pedido","finalizar","pagar","confirmar"],
    respostas=["..."],gera_ctx="pagando",acao=fechar)
bot.treinar_intent("pagar_d",frases=["pix","cartao","dinheiro","boleto","pagar com"],
    respostas=["..."],exige_ctx="pagando",acao=pagar)

print(f"\n{Fore.YELLOW}=== SIMULANDO DELIVERY ==={Style.RESET_ALL}\n")
bot.simular(["cardapio","x-bacon","batata","refrigerante","ver carrinho",
             "tenho cupom DESC10","fechar pedido","pagar com pix"])


# ════════════════════════════════════════════════════════════
#  PONTO DE ENTRADA
#  Ao rodar com F5 / ▶, testes aparecem e chat abre em seguida!
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print()
    bot.chat()
