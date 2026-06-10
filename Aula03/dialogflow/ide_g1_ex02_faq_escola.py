# ╔══════════════════════════════════════════════════════════╗
# ║  🏫  Bot FAQ da Escola                             ║
# ║  Nivel: Facil                                            ║
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
#     Responde perguntas frequentes sobre a escola — horario das aulas,
#     data de provas, tarefas, cantina e falta de professor.
#     E o tipo de bot que a secretaria adoraria ter!
#  
#  Conceito ensinado — ENTIDADES:
#     Entidade e uma informacao especifica DENTRO da frase do usuario.
#     Quando o aluno pergunta "prova de matematica quando e?":
#       → Intent: data_prova (o usuario quer saber sobre prova)
#       → Entidade: matematica (QUAL materia especificamente)
#  
#  Pense assim:
#     Um formulario de pedido de pizza. O Intent e "quero pizza"
#     e as entidades sao os detalhes: sabor=calabresa, tamanho=G.
#     A entidade extrai o DETALHE especifico da mensagem!
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
#  2. Digite: python g1_ex02_faq_escola.py
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

MATERIAS = [
    "matematica", "portugues", "historia", "geografia",
    "ingles", "fisica", "quimica", "programacao",
]

bot = MiniDialogflow("EscolaBot")

bot.treinar_intent(
    nome="horario_aulas",
    frases=["que horas comeca a aula", "horario das aulas",
            "que horas e a aula", "quando comeca a aula",
            "horario escolar", "que horas tenho aula",
            "que horas abre a escola"],
    respostas=[
        "Horarios:\n"
        "  Manha: 7h30 as 12h\n"
        "  Tarde : 13h30 as 17h30"
    ]
)

bot.treinar_intent(
    nome="data_prova",
    frases=["quando e a prova", "data da prova", "tem prova essa semana",
            "quando e a avaliacao", "prova de matematica",
            "prova de portugues", "prova de programacao"],
    # entidades: o bot vai EXTRAIR a materia da frase
    entidades=[{"nome": "materia", "valores": MATERIAS}],
    respostas=[
        "Para a prova de {materia}: consulte o portal do aluno!",
        "Datas de provas: acesse o portal ou pergunte ao professor.",
    ]
)

bot.treinar_intent(
    nome="tarefa",
    frases=[
        "qual e a tarefa", "licao de casa", "dever de casa",
        "tem dever", "qual e o dever", "atividade para casa",
        "o que e tarefa", "que dever tenho", "tem para casa",
        "tarefa de hoje", "que atividade", "qual e o trabalho",
    ],
    respostas=["As tarefas ficam no Google Classroom! Ja acessou hoje?"]
)

bot.treinar_intent(
    nome="cantina",
    frases=["o que tem na cantina", "cardapio da cantina",
            "o que tem para comer", "cantina ta aberta",
            "cardapio hoje", "quanto custa o lanche"],
    respostas=[
        "Cantina aberta das 7h as 17h!\n"
        "Hoje tem pao de queijo, salgados, suco e refrigerante."
    ]
)

bot.treinar_intent(
    nome="falta_professor",
    frases=["o professor faltou", "tem aula hoje", "vai ter aula",
            "aula foi cancelada", "o professor nao veio"],
    respostas=["Para saber de cancelamentos, consulte a secretaria ou o app da escola!"]
)

# ════════════════════════════════════════════════════════════
#  TESTES AUTOMATICOS (rodam ao executar o arquivo)
# ════════════════════════════════════════════════════════════

print(f"\n{Fore.YELLOW}{'='*50}")
print("  TESTES AUTOMATICOS — PERGUNTAS DE ALUNOS")
print(f"{'='*50}{Style.RESET_ALL}\n")

perguntas = [
    ("que horas comeca a aula", "horario_aulas"),
    ("quando e a prova de matematica", "data_prova"),
    ("qual e o dever de casa", "tarefa"),
    ("o que tem na cantina", "cantina"),
    ("o professor veio hoje", "falta_professor"),
]
certos = 0
for msg, esperado in perguntas:
    r = bot.detectar(msg)
    ok = r["intent"] == esperado
    certos += int(ok)
    print(f"  {'✓' if ok else '✗'} Aluno: '{msg}'")
    print(f"     Bot: '{r['resposta'][:70]}'")
    if r["entidades"]:
        print(f"     Entidade detectada: {r['entidades']}")
    print()

print(f"  Placar: {certos}/{len(perguntas)} corretos")

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
