# ╔══════════════════════════════════════════════════════════╗
# ║  🎪  Bot de Eventos e Ingressos                    ║
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
#     Lista eventos, permite escolher um, informar a quantidade de ingressos
#     e finaliza a compra com codigo de confirmacao.
#  
#  Conceito ensinado — SLOT FILLING:
#     Slot Filling e a coleta estruturada de dados obrigatorios.
#     Como um formulario digital que o bot vai preenchendo durante
#     a conversa — um "campo" (slot) por vez.
#  
#  Pense assim:
#     e como comprar passagem de aviao online: origem, destino, data,
#     passageiros, pagamento — cada um em seu momento.
#     O bot conduz o usuario por essa jornada conversacionalmente!
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
#  2. Digite: python g1_ex09_eventos.py
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

# Banco de eventos simulado
EVENTOS = {
    "show-rock"    : {"nome": "Rock no Parque",     "data": "15/08", "preco": 120},
    "workshop-py"  : {"nome": "Workshop Python+IA", "data": "22/08", "preco": 250},
    "teatro"       : {"nome": "Hamlet — Teatro",    "data": "25/08", "preco": 80},
}

reservas    = {}
slots_compra = {}

def listar_eventos(msg, dados):
    linhas = ["Eventos disponiveis:\n"]
    for ev in EVENTOS.values():
        linhas.append(f"  🎪 {ev['nome']}")
        linhas.append(f"     {ev['data']} | R${ev['preco']} por ingresso\n")
    return "\n".join(linhas) + "\nQual evento te interessa?"

def selecionar_evento(msg, dados):
    for key, ev in EVENTOS.items():
        palavras = [key.split("-")[0], ev["nome"].split()[0].lower()]
        if any(p in msg.lower() for p in palavras):
            slots_compra["evento"] = ev
            return (f"Otima escolha! {ev['nome']} 🎪\n"
                    f"Data: {ev['data']} | R${ev['preco']} por ingresso\n\n"
                    f"Quantos ingressos? (maximo 4)")
    return "Qual evento? Diz o nome ou parte dele."

def reservar_ingressos(msg, dados):
    nums = re.findall(r"\d+", msg)
    qtd  = min(int(nums[0]), 4) if nums else 1
    ev   = slots_compra.get("evento", {})
    total = qtd * ev.get("preco", 0)
    codigo = f"ING-{random.randint(100000, 999999)}"
    reservas[codigo] = {"evento": ev.get("nome"), "qtd": qtd, "total": total}
    return (f"COMPRA CONFIRMADA! ✅\n\n"
            f"Codigo: {codigo}\n"
            f"Evento: {ev.get('nome')}\n"
            f"Ingressos: {qtd} x R${ev.get('preco', 0):.2f}\n"
            f"Total: R${total:.2f}\n\n"
            f"Ingressos enviados por e-mail!")

bot = MiniDialogflow("EventoBot")

bot.treinar_intent(
    nome="ver_eventos",
    frases=["quais eventos tem", "o que vai ter", "agenda",
            "shows", "eventos", "ver eventos", "programacao"],
    respostas=["Buscando eventos..."],
    acao=listar_eventos,
    gera_ctx="escolhendo_evento"
)

bot.treinar_intent(
    nome="selecionar_evento",
    frases=["rock", "workshop", "teatro", "python", "show",
            "quero ir", "esse aqui", "quero o"],
    respostas=["Verificando disponibilidade..."],
    exige_ctx="escolhendo_evento",
    gera_ctx="escolhendo_quantidade",
    acao=selecionar_evento
)

bot.treinar_intent(
    nome="escolher_quantidade",
    frases=["1", "2", "3", "4", "um", "dois", "tres", "quatro", "quero"],
    respostas=["Processando reserva..."],
    exige_ctx="escolhendo_quantidade",
    acao=reservar_ingressos
)

# ════════════════════════════════════════════════════════════
#  TESTES AUTOMATICOS (rodam ao executar o arquivo)
# ════════════════════════════════════════════════════════════

print(f"\n{Fore.YELLOW}{'='*50}")
print("  SIMULANDO COMPRA DE INGRESSO")
print(f"{'='*50}{Style.RESET_ALL}\n")

for msg in ["quais eventos tem", "workshop python", "2 ingressos"]:
    r = bot.detectar(msg)
    print(f"  Voce: '{msg}'")
    print(f"  Bot : '{r['resposta'][:100]}'\n")

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
