# ╔══════════════════════════════════════════════════════════╗
# ║  📚  Bot FAQ Escola Completo (9 topicos)           ║
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
#     Versao expandida do FAQ com 9 topicos: horarios, provas, tarefas,
#     cantina, matricula, uniforme, transporte, biblioteca e aula do dia.
#  
#  Como e diferente do Grupo 1:
#     G1 tinha 4 topicos (horario, prova, tarefa, cantina).
#     G2 tem 9 topicos + mais frases de treino por intent.
#     Quanto mais intents, mais situacoes o bot cobre!
#  
#  Dica de estudo:
#     Este arquivo e um otimo template para criar um FAQ real.
#     Adapte os topicos para a sua escola, empresa ou projeto!
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
#  2. Digite: python g2_ex02_faq_escola_completo.py
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

MATERIAS = ["matematica", "portugues", "historia", "ingles",
            "fisica", "quimica", "programacao"]
DIAS     = ["segunda", "terca", "quarta", "quinta", "sexta"]

bot = MiniDialogflow("EscolaBot")

bot.treinar_intent(
    nome="horario_aulas",
    frases=["que horas comeca a aula", "horario das aulas",
            "horario escolar", "que horas e a aula",
            "quando comeca a aula", "que horas abre a escola"],
    respostas=["Horarios:\n  Manha: 7h30 as 12h\n  Tarde: 13h30 as 17h30"]
)

bot.treinar_intent(
    nome="data_prova",
    frases=["quando e a prova", "data da prova", "tem prova",
            "quando e avaliacao", "prova de matematica",
            "prova de portugues", "prova de fisica"],
    entidades=[{"nome": "materia", "valores": MATERIAS}],
    respostas=["Para {materia}: consulte o portal do aluno!",
               "Datas de provas: acesse o portal ou pergunte ao professor."]
)

bot.treinar_intent(
    nome="tarefa",
    frases=["qual e a tarefa", "tem licao de casa", "tem dever",
            "tem atividade para casa", "tem trabalho"],
    respostas=["Tarefas ficam no Google Classroom! Ja acessou hoje?"]
)

bot.treinar_intent(
    nome="cantina",
    frases=["o que tem na cantina", "cardapio", "cantina aberta",
            "o que tem para comer", "quanto custa o lanche"],
    respostas=["Cantina: 7h as 17h! Hoje: pao de queijo, salgados e bebidas."]
)

bot.treinar_intent(
    nome="matricula",
    frases=["como faz matricula", "documentos para matricula",
            "renovar matricula", "rematricula", "quais documentos"],
    respostas=["Matricula: RG, CPF e comprovante de residencia. Va a secretaria!"]
)

bot.treinar_intent(
    nome="uniforme",
    frases=["precisa de uniforme", "escola tem uniforme",
            "uniforme obrigatorio", "como e o uniforme"],
    respostas=["Uniforme e obrigatorio: camiseta azul + calca/bermuda cinza."]
)

bot.treinar_intent(
    nome="transporte",
    frases=["tem onibus escolar", "transporte", "como ir ate a escola", "van escolar"],
    respostas=["Transporte disponivel! Fale com a secretaria para se cadastrar."]
)

bot.treinar_intent(
    nome="biblioteca",
    frases=["biblioteca aberta", "horario da biblioteca",
            "posso pegar livro", "emprestimo de livro"],
    respostas=["Biblioteca: seg a sex, 7h30 as 17h. Leve a carteirinha!"]
)

bot.treinar_intent(
    nome="aula_do_dia",
    frases=["quais aulas hoje", "grade de hoje", "materia de segunda",
            "aula de terca", "o que tem hoje", "quais sao as aulas"],
    entidades=[{"nome": "dia", "valores": DIAS}],
    respostas=["Grade de {dia}: acesse o portal ou veja sua grade impressa!",
               "Para ver as aulas do dia: portal do aluno!"]
)

# ════════════════════════════════════════════════════════════
#  TESTES AUTOMATICOS (rodam ao executar o arquivo)
# ════════════════════════════════════════════════════════════

print(f"\n{Fore.YELLOW}{'='*50}")
print("  TESTANDO 9 PERGUNTAS ESCOLARES")
print(f"{'='*50}{Style.RESET_ALL}\n")

perguntas = [
    ("que horas comeca a aula",      "horario_aulas"),
    ("quando e a prova de fisica",   "data_prova"),
    ("tem tarefa para hoje",          "tarefa"),
    ("uniforme e obrigatorio",        "uniforme"),
    ("quais aulas tem segunda",       "aula_do_dia"),
    ("posso pegar livro na biblioteca","biblioteca"),
]
certos = 0
for msg, esp in perguntas:
    r = bot.detectar(msg)
    ok = r["intent"] == esp
    certos += int(ok)
    print(f"  {'✓' if ok else '✗'} '{msg}'")
    print(f"     → '{r['resposta'][:60]}'\n")

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
