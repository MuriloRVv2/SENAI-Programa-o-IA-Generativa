# ╔══════════════════════════════════════════════════════════╗
# ║  🏢  Bot SAC Enterprise                            ║
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
#    Sistema de atendimento completo com roteamento inteligente,
#    fila de prioridade por sentimento, SLA e rastreamento de protocolo.
# 
#    Diferenca do Grupo 1:
#    O SAC basico apenas abria protocolos. Este rastreia a fila de
#    atendimento, define prioridade baseada no sentimento do cliente
#    (negativo = urgente, positivo = normal) e tem SLA definido.
# 
#    Conceito ensinado: SENTIMENTO como GATILHO DE NEGOCIO
#    Detectar que o cliente esta com raiva e tratar como URGENTE
#    e uma pratica real em empresas — o Dialogflow suporta isso nativamente!
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
#  2. Digite: python g2_ex11_sac_enterprise.py
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
#  CODIGO DO EXEMPLO: Bot SAC Enterprise
# ════════════════════════════════════════════════════════════

from collections import defaultdict
protocolos={}; fila=defaultdict(list)
PALAVRAS_NEG={"ruim","pessimo","absurdo","horrivel","raiva","indignado","inadmissivel"}

def sentimento(msg):
    return "negativo" if set(msg.lower().split()) & PALAVRAS_NEG else "positivo"

def reclamacao(msg,dados):
    sent=sentimento(msg); prio="URGENTE" if sent=="negativo" else "NORMAL"
    sla="2h" if prio=="URGENTE" else "48h"; prot=f"REC-{random.randint(100000,999999)}"
    protocolos[prot]={"tipo":"reclamacao","prio":prio,"status":"aberto"}
    fila["urgente" if prio=="URGENTE" else "normal"].append(prot)
    return (f"{'🚨' if prio=='URGENTE' else '📋'} Reclamacao registrada!\n"
            f"Protocolo: {prot} | Prioridade: {prio} | SLA: {sla}")

def elogio(msg,dados):
    prot=f"ELO-{random.randint(100000,999999)}"
    protocolos[prot]={"tipo":"elogio","status":"registrado"}
    return f"🌟 Elogio registrado ({prot})! Obrigado! Repassando para a equipe!"

def cancelar(msg,dados):
    return ("Por que deseja cancelar?\n"
            "A) Preco alto\nB) Nao uso mais\nC) Mau atendimento\nD) Outro")

def rastrear(msg,dados):
    prots=re.findall(r"(?:REC|SOL|ELO|CAN)-\d+",msg.upper())
    if not prots: return "Me passa o protocolo! Formato: REC-123456"
    p=prots[0]
    if p not in protocolos: return f"Protocolo {p} nao encontrado."
    d=protocolos[p]
    return f"Protocolo {p}:\n  Tipo: {d['tipo'].title()}\n  Status: {d['status'].upper()}"

def ver_fila(msg,dados):
    return (f"Fila:\n  Urgente: {len(fila['urgente'])} casos\n"
            f"  Normal: {len(fila['normal'])} casos\n"
            f"  Total protocolos: {len(protocolos)}")

bot=MiniDialogflow("SACEnterprise")
bot.treinar_intent("boas_vindas",frases=["oi","ola","preciso de ajuda","atendimento","suporte"],
    respostas=["Ola! SAC Virtual.\n1.Reclamacao 2.Elogio 3.Cancelamento 4.Rastrear 5.Humano"])
bot.treinar_intent("reclamacao",frases=["reclamar","insatisfeito","problema","defeito",
    "absurdo","nao funcionou","1"],respostas=["..."],acao=reclamacao)
bot.treinar_intent("elogio",frases=["elogio","adorei","excelente","muito bom","parabens","2"],
    respostas=["..."],acao=elogio)
bot.treinar_intent("cancelar",frases=["cancelar","nao quero mais","encerrar","3"],
    respostas=["..."],acao=cancelar)
bot.treinar_intent("rastrear",frases=["acompanhar protocolo","status","meu protocolo","4"],
    respostas=["..."],acao=rastrear)
bot.treinar_intent("humano",frases=["humano","atendente","pessoa","5"],
    respostas=["Transferindo! ⏳ Espera: ~5 minutos."])
bot.treinar_intent("fila",frases=["ver fila","status atendimento","relatorio"],
    respostas=["..."],acao=ver_fila)

print(f"\n{Fore.YELLOW}=== SIMULANDO SAC ENTERPRISE ==={Style.RESET_ALL}\n")
for msg in ["oi preciso de ajuda","quero reclamar esse produto e um absurdo",
            "adorei o atendimento parabens","quero cancelar","ver fila"]:
    r=bot.detectar(msg)
    print(f"  Cliente: '{msg}'\n  Bot    : '{r['resposta']}'\n")


# ════════════════════════════════════════════════════════════
#  PONTO DE ENTRADA
#  Ao rodar com F5 / ▶, testes aparecem e chat abre em seguida!
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print()
    bot.chat()
