# ╔══════════════════════════════════════════════════════════╗
# ║  🎓  Bot Assistente de Estudos                     ║
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
#    Assistente de estudos com flashcards de 3 materias, plano semanal
#    personalizado e tecnica Pomodoro integrada.
# 
#    Conceito ensinado: BOT EDUCACIONAL com ESTADO COMPLEXO
#    Um bot educacional precisa rastrear: qual materia esta estudando,
#    quantos flashcards ja respondeu, quantos acertou e qual e o proximo.
#    Isso demanda gerenciamento de estado sofisticado entre turnos.
# 
#    Pense assim:
#    e como um tutor virtual. Ele sabe onde voce parou na ultima sessao,
#    quais topicos voce tem dificuldade e adapta as proximas questoes.
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
#  2. Digite: python g2_ex12_assistente_estudos.py
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
#  CODIGO DO EXEMPLO: Bot Assistente de Estudos
# ════════════════════════════════════════════════════════════

from collections import defaultdict
FLASHCARDS={
    "python":[
        {"p":"O que e uma lista em Python?","r":"colecao mutavel entre colchetes"},
        {"p":"Diferenca entre = e ==?","r":"= atribui, == compara"},
        {"p":"O que e uma funcao lambda?","r":"funcao anonima de uma linha"},
    ],
    "ia":[
        {"p":"O que e Machine Learning?","r":"ia que aprende com dados"},
        {"p":"O que e overfitting?","r":"decora treino mas falha no teste"},
        {"p":"Para que serve dropout?","r":"desliga neuronios no treino"},
    ],
    "matematica":[
        {"p":"O que e derivada?","r":"taxa de variacao da funcao"},
        {"p":"O que e probabilidade?","r":"chance de evento: 0 impossivel, 1 certo"},
        {"p":"O que e pitagoras?","r":"a2 mais b2 igual c2"},
    ],
}
progresso=defaultdict(lambda:{"acertos":0,"erros":0})
estado_fc={"cards":[],"idx":0,"mat":"","rodando":False}

def iniciar_fc(msg,dados):
    mat=next((m for m in FLASHCARDS if m in msg.lower()),"python")
    cards=FLASHCARDS[mat].copy(); random.shuffle(cards)
    estado_fc.update({"cards":cards,"idx":0,"mat":mat,"rodando":True})
    return f"Flashcards de {mat.upper()}!\nPergunta 1/{len(cards)}:\n{cards[0]['p']}"

def ver_resp(msg,dados):
    if not estado_fc["rodando"] or estado_fc["idx"]>=len(estado_fc["cards"]):
        return "Inicia com 'flashcard de [materia]'!"
    return f"Resposta: {estado_fc['cards'][estado_fc['idx']]['r']}\n\nAcertou? Diz 'acertei' ou 'errei'!"

def avaliar_fc(msg,dados):
    ok=any(p in msg for p in ["acert","correto","sabia","lembrei"])
    mat=estado_fc["mat"]
    if ok: progresso[mat]["acertos"]+=1; fb="✅ Otimo!"
    else:  progresso[mat]["erros"]+=1;   fb="📚 Anote pra revisar!"
    estado_fc["idx"]+=1
    if estado_fc["idx"]<len(estado_fc["cards"]):
        prox=estado_fc["cards"][estado_fc["idx"]]
        return f"{fb}\nPergunta {estado_fc['idx']+1}/{len(estado_fc['cards'])}:\n{prox['p']}"
    ac=progresso[mat]["acertos"]; er=progresso[mat]["erros"]
    pct=ac/(ac+er)*100 if (ac+er) else 0
    estado_fc["rodando"]=False
    return (f"{fb}\nFIM! {mat.upper()}: {ac}✅ {er}❌ ({pct:.0f}%)\n"
            f"{'Excelente!' if pct>=80 else 'Continue praticando!'}")

def criar_plano(msg,dados):
    mats=[m for m in FLASHCARDS if m in msg.lower()]
    if not mats: return "Quais materias quer estudar? (python, ia, matematica)"
    dias=["Segunda","Terca","Quarta","Quinta","Sexta"]
    return ("Plano semanal:\n" +
            "\n".join(f"  {dias[i%5]}: {m.upper()}" for i,m in enumerate(mats)))

def pomodoro(msg,dados):
    tipo="pausa" if any(p in msg for p in ["pausa","descanso"]) else "foco"
    dur=5 if tipo=="pausa" else 25
    return f"{'⏸ Pausa' if tipo=='pausa' else '🍅 FOCO'}: {dur} minutos!\n{'Descanse!' if tipo=='pausa' else 'Sem celular, sem distracao!'}"

bot=MiniDialogflow("EstudoBot")
bot.treinar_intent("flashcard",frases=["flashcard","revisar python","revisar ia",
    "revisar matematica","estudar com cards"],respostas=["Iniciando!"],
    gera_ctx="fc_ativo",acao=iniciar_fc)
bot.treinar_intent("ver_resp",frases=["resposta","ver resposta","mostrar","revelar"],
    respostas=["..."],exige_ctx="fc_ativo",acao=ver_resp)
bot.treinar_intent("avaliar",frases=["acertei","errei","nao sabia","sabia","lembrei"],
    respostas=["..."],exige_ctx="fc_ativo",acao=avaliar_fc)
bot.treinar_intent("plano",frases=["plano de estudos","organizar estudos","criar plano"],
    respostas=["..."],acao=criar_plano)
bot.treinar_intent("pomodoro",frases=["pomodoro","foco","pausa","descanso","25 minutos"],
    respostas=["..."],acao=pomodoro)

print(f"\n{Fore.YELLOW}=== SESSAO DE ESTUDOS ==={Style.RESET_ALL}\n")
for msg in ["flashcard de python","resposta","acertei","resposta","errei",
            "plano python e ia","pomodoro foco"]:
    r=bot.detectar(msg)
    print(f"  Voce: '{msg}'\n  Bot : '{r['resposta'][:80]}'\n")


# ════════════════════════════════════════════════════════════
#  PONTO DE ENTRADA
#  Ao rodar com F5 / ▶, testes aparecem e chat abre em seguida!
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print()
    bot.chat()
