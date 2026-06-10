# ╔══════════════════════════════════════════════════════════╗
# ║  💰  Bot Financeiro Pessoal                        ║
# ║  Nivel: Avancado                                         ║
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
#    Assistente financeiro pessoal que registra gastos por categoria,
#    controla orcamentos com alertas e gerencia metas de poupanca.
# 
#    Conceito ensinado: BOT COMO FERRAMENTA DE PRODUTIVIDADE
#    Chatbots nao servem so para atendimento — eles podem ser ferramentas
#    pessoais de produtividade. Um bot financeiro e um caso de uso real
#    que muitas fintechs estao implementando hoje.
# 
#    Pense assim:
#    e como um caderninho de anotacoes que FALA COM VOCE.
#    Em vez de anotar "gastei R$50 no ifood", voce manda mensagem
#    e o bot registra, categoriza e te avisa se passou do limite!
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
#  2. Digite: python g2_ex13_financeiro.py
#  3. Pronto!
#
#  INSTALACAO (so na primeira vez — no terminal do projeto):
#    pip install pip install colorama
#
#  DURANTE O CHAT:
#    sair  → encerra o chat
#    reset → comeca uma nova conversa
# ════════════════════════════════════════════════════════════

import re, random
from colorama import Fore, Style, init; init(autoreset=True)

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
#  CODIGO DO EXEMPLO: Bot Financeiro Pessoal
# ════════════════════════════════════════════════════════════

from collections import defaultdict
CATEGORIAS=["alimentacao","transporte","lazer","saude","educacao","moradia","outro"]
MAPA_CAT={"alimentacao":["lanche","comida","restaurante","mercado","ifood"],
           "transporte":["uber","onibus","gasolina","metro","carro"],
           "lazer":["cinema","show","jogo","festa","bar"],
           "saude":["farmacia","medico","remedio","academia"],
           "educacao":["curso","livro","faculdade","material"]}
gastos=[]; receitas=[]; orcamento={}; metas={}

def reg_gasto(msg,dados):
    vals=re.findall(r"\d+[.,]?\d*",msg)
    v=float(vals[0].replace(",",".")) if vals else 0
    if v==0: return "Qual o valor? Ex: 'gastei 50 no almoco'"
    cat="outro"
    for c,palavras in MAPA_CAT.items():
        if any(p in msg.lower() for p in palavras): cat=c; break
    gastos.append({"valor":v,"cat":cat})
    total_cat=sum(g["valor"] for g in gastos if g["cat"]==cat)
    lim=orcamento.get(cat,0)
    alerta=f"\n⚠️ LIMITE de R${lim:.0f} atingido para {cat}!" if lim and total_cat>=lim else ""
    return f"✅ R${v:.2f} em {cat.upper()} registrado! Total {cat}: R${total_cat:.2f}{alerta}"

def reg_receita(msg,dados):
    vals=re.findall(r"\d+[.,]?\d*",msg)
    v=float(vals[0].replace(",",".")) if vals else 0
    if v==0: return "Qual o valor recebido?"
    receitas.append({"valor":v})
    return f"✅ Receita de R${v:.2f} registrada! Total: R${sum(r['valor'] for r in receitas):.2f}"

def resumo(msg,dados):
    if not gastos: return "Nenhum gasto registrado ainda!"
    tg=sum(g["valor"] for g in gastos); tr=sum(r["valor"] for r in receitas)
    por_cat=defaultdict(float)
    for g in gastos: por_cat[g["cat"]]+=g["valor"]
    linhas=[f"Resumo:\n  Receitas: R${tr:.2f}\n  Gastos: R${tg:.2f}\n  Saldo: R${tr-tg:.2f}\n\nPor categoria:"]
    mx=max(por_cat.values()) if por_cat else 1
    for cat,val in sorted(por_cat.items(),key=lambda x:-x[1]):
        barra="█"*int(val/mx*12); lim=orcamento.get(cat,0)
        alerta="⚠" if lim and val>=lim else " "
        linhas.append(f"  {alerta} {cat.upper():<15} R${val:>7.2f} {barra}")
    return "\n".join(linhas)

def def_orc(msg,dados):
    vals=re.findall(r"\d+[.,]?\d*",msg); v=float(vals[0].replace(",",".")) if vals else 0
    cat="outro"
    for c in CATEGORIAS:
        if c in msg.lower(): cat=c; break
    if v==0: return "Qual o limite para qual categoria?"
    orcamento[cat]=v; return f"✅ Limite de R${v:.2f} para {cat.upper()} definido!"

def criar_meta(msg,dados):
    vals=re.findall(r"\d+[.,]?\d*",msg); v=float(vals[0].replace(",",".")) if vals else 0
    if v==0: return "Qual o valor da meta? Ex: 'meta viagem 3000'"
    nome=msg.split()[1] if len(msg.split())>1 else "meta"
    metas[nome]={"obj":v,"atual":0}
    return f"🎯 Meta '{nome}': R${v:.2f} criada!"

def contribuir(msg,dados):
    vals=re.findall(r"\d+[.,]?\d*",msg); v=float(vals[0].replace(",",".")) if vals else 0
    if not metas: return "Crie uma meta primeiro!"
    for nome,meta in metas.items():
        if nome in msg.lower():
            meta["atual"]+=v; pct=meta["atual"]/meta["obj"]*100
            return (f"✅ R${v:.2f} para '{nome}'!\n"
                    f"Progresso: R${meta['atual']:.2f}/{meta['obj']:.2f} ({pct:.0f}%)\n"
                    f"{'🏆 META ATINGIDA!' if pct>=100 else f'Faltam R${meta["obj"]-meta["atual"]:.2f}'}")
    return f"Meta nao encontrada. Metas: {', '.join(metas.keys())}"

bot=MiniDialogflow("FinanceBot")
bot.treinar_intent("gasto",frases=["gastei","comprei","paguei","despesa","saiu"],
    respostas=["..."],acao=reg_gasto)
bot.treinar_intent("receita",frases=["recebi","salario","ganhei","entrada","freelance"],
    respostas=["..."],acao=reg_receita)
bot.treinar_intent("resumo",frases=["resumo","financas","quanto gastei","saldo","extrato"],
    respostas=["..."],acao=resumo)
bot.treinar_intent("orcamento",frases=["limite","orcamento","definir limite"],
    respostas=["..."],acao=def_orc)
bot.treinar_intent("meta",frases=["quero juntar","meta","objetivo","economizar para"],
    respostas=["..."],acao=criar_meta)
bot.treinar_intent("guardar",frases=["guardar","poupar","contribuir para minha meta"],
    respostas=["..."],acao=contribuir)

print(f"\n{Fore.YELLOW}=== CONTROLE FINANCEIRO ==={Style.RESET_ALL}\n")
for msg in ["recebi 3000 de salario","gastei 45 no ifood almoco",
            "gastei 200 no mercado alimentacao","limite alimentacao 500",
            "meta viagem 5000","guardar 200 para viagem","resumo financeiro"]:
    r=bot.detectar(msg)
    print(f"  Voce: '{msg}'\n  Bot : '{r['resposta'][:90]}'\n")


# ════════════════════════════════════════════════════════════
#  PONTO DE ENTRADA
#  Ao rodar com F5 / ▶, testes aparecem e chat abre em seguida!
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print()
    bot.chat()
