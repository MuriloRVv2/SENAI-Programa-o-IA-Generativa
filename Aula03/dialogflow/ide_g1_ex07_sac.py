# ╔══════════════════════════════════════════════════════════╗
# ║  📞  Bot SAC Completo                              ║
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
#  O que este bot faz:
#     Um sistema de atendimento ao cliente com menu, roteamento por
#     departamento e geracao automatica de numeros de protocolo.
#  
#  Conceito ensinado — ROTEAMENTO de FLUXO:
#     Um SAC real precisa identificar o tipo de atendimento e direcionar
#     para o fluxo correto. O contexto diz em qual etapa o cliente esta.
#  
#  Conceito ensinado — FULFILLMENT com logica de negocio:
#     O bot nao apenas responde texto — ele GERA protocolos, REGISTRA
#     atendimentos e pode CALCULAR prazos automaticamente.
#  
#  Pense assim:
#     e como a URA do banco ("Para saldo, digita 1..."). So que em vez
#     de numeros, o cliente fala naturalmente e o bot entende!
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
#  2. Digite: python g1_ex07_sac.py
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

# Banco de dados simples (em memoria)
protocolos = {}

def abrir_reclamacao(msg, dados):
    protocolo = f"REC-{random.randint(100000, 999999)}"
    protocolos[protocolo] = {"tipo": "reclamacao", "msg": msg, "status": "aberto"}
    return (f"Reclamacao registrada! 📋\n\n"
            f"Protocolo: {protocolo}\n"
            f"Prazo: retorno em ate 48h.\n\n"
            f"Me conta o que aconteceu para detalharmos o caso.")

def registrar_elogio(msg, dados):
    protocolo = f"ELO-{random.randint(100000, 999999)}"
    protocolos[protocolo] = {"tipo": "elogio", "status": "registrado"}
    return (f"Elogio registrado! 🌟 ({protocolo})\n"
            f"Obrigado pelo feedback! Vou repassar para toda a equipe!")

def iniciar_cancelamento(msg, dados):
    return ("Por que deseja cancelar? 😢\n\n"
            "A) Preco muito alto\n"
            "B) Nao uso mais o servico\n"
            "C) Fui mal atendido\n"
            "D) Outro motivo")

def rastrear_protocolo(msg, dados):
    prots = re.findall(r"(?:REC|ELO|CAN)-\d+", msg.upper())
    if not prots:
        return "Me passa o numero do protocolo! Formato: REC-123456"
    p = prots[0]
    if p not in protocolos:
        return f"Protocolo {p} nao encontrado. Verifique o numero."
    d = protocolos[p]
    return (f"Protocolo: {p}\n"
            f"Tipo: {d['tipo'].title()}\n"
            f"Status: {d['status'].upper()}")

bot = MiniDialogflow("SACBot")

bot.treinar_intent(
    nome="boas_vindas",
    frases=["oi", "ola", "preciso de ajuda", "suporte", "falar com sac", "preciso ajuda"],
    respostas=["Ola! Sou o assistente virtual. Como posso ajudar?\n\n"
               "1️⃣ Reclamacao\n2️⃣ Elogio\n3️⃣ Cancelamento\n"
               "4️⃣ Rastrear protocolo\n5️⃣ Falar com humano"]
)

bot.treinar_intent(
    nome="reclamacao",
    frases=["reclamacao", "quero reclamar", "insatisfeito", "problema",
            "defeito", "nao funcionou", "errado", "1"],
    respostas=["Registrando reclamacao..."],
    acao=abrir_reclamacao
)

bot.treinar_intent(
    nome="elogio",
    frases=[
        "elogio", "adorei", "amei", "excelente atendimento",
        "muito bom", "parabens", "maravilha", "satisfeito",
        "otimo servico", "fui bem atendido", "adorei atendimento",
        "quero elogiar", "nota 10", "top", "perfeito", "2",
    ],
    respostas=["Registrando elogio!"],
    acao=registrar_elogio
)

bot.treinar_intent(
    nome="cancelar",
    frases=["cancelar", "encerrar contrato", "nao quero mais", "cancelamento", "3"],
    respostas=["Abrindo cancelamento..."],
    acao=iniciar_cancelamento
)

bot.treinar_intent(
    nome="rastrear",
    frases=["rastrear", "acompanhar protocolo", "status", "meu protocolo", "4"],
    respostas=["Buscando protocolo..."],
    acao=rastrear_protocolo
)

bot.treinar_intent(
    nome="humano",
    frases=["humano", "atendente", "pessoa real", "falar com pessoa", "5"],
    respostas=["Transferindo para atendente humano! 👤\n"
               "⏳ Tempo de espera: ~5 minutos."]
)

# ════════════════════════════════════════════════════════════
#  TESTES AUTOMATICOS (rodam ao executar o arquivo)
# ════════════════════════════════════════════════════════════

print(f"\n{Fore.YELLOW}{'='*50}")
print("  SIMULANDO ATENDIMENTO SAC")
print(f"{'='*50}{Style.RESET_ALL}\n")

for msg in ["oi preciso de ajuda",
            "quero reclamar do produto",
            "adorei atendimento quero elogiar",
            "quero cancelar"]:
    r = bot.detectar(msg)
    print(f"  Cliente: '{msg}'")
    print(f"  Bot    : '{r['resposta'][:80]}'\n")

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
