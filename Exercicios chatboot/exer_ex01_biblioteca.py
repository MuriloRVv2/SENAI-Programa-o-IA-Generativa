# ╔══════════════════════════════════════════════════════════╗
# ║  📚  EXERCICIO 1 — Bot da Biblioteca Municipal          ║
# ║  Nivel: Facil  |  Base: Exemplos 01 e 02               ║
# ╚══════════════════════════════════════════════════════════╝
#
# ════════════════════════════════════════════════════════════
#  GABARITO — resultado esperado apos o uso do prompt
# ════════════════════════════════════════════════════════════
#
# CONTEXTO DO EXERCICIO:
#   Voce e o responsavel de TI de uma biblioteca escolar.
#   O diretor pediu um chatbot para atender os alunos e
#   responder as perguntas mais frequentes.
#
# O QUE O BOT DEVE FAZER:
#   Responder sobre 5 topicos da biblioteca:
#   1. Horario de funcionamento
#   2. Como fazer emprestimo de livros
#   3. Prazo de devolucao e renovacao
#   4. Multa por atraso
#   5. Eventos literarios (clube do livro)
#
# PROMPT QUE GEROU ESTE CODIGO:
#   "Crie um chatbot em Python usando a classe MiniDialogflow
#    para ser a recepcionista virtual da Biblioteca Escolar.
#    O bot deve responder sobre:
#    - Horario: seg-sex 7h30-17h, sabado 8h-12h
#    - Emprestimo: precisa de carteirinha, maximo 2 livros
#    - Prazo: 7 dias, pode renovar 1 vez pessoalmente ou pelo chat
#    - Multa: R$0,50 por dia de atraso
#    - Clube do livro: toda terca as 15h, aberto a todos
#    Use pelo menos 6 frases de treino por intent.
#    Inclua a classe MiniDialogflow completa no arquivo.
#    Ao final, chame bot.chat() para o usuario interagir."
#
# INSTALACAO:  pip install colorama
# COMO RODAR:  python ex01_biblioteca.py
# ════════════════════════════════════════════════════════════

import re
import random
from colorama import Fore, Style, init
init(autoreset=True)


class MiniDialogflow:
    """Simula o Dialogflow — versao basica com context-aware fallback."""

    def __init__(self, nome):
        self.nome = nome
        self.intents = {}
        self.contexto = None
        self.dados = {}

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

    def detectar(self, msg):
        ml = msg.lower().strip()
        melhor, score = None, 0.0
        for nome, intent in self.intents.items():
            if intent["exige_ctx"] and self.contexto != intent["exige_ctx"]:
                continue
            for frase in intent["frases"]:
                pf = set(frase.split()); pm = set(ml.split())
                s = len(pm & pf) / len(pm | pf) if (pm | pf) else 0
                if frase in ml: s = max(s, 0.85)
                if s > score: score, melhor = s, nome
        if not (melhor and score >= 0.18):
            if self.contexto:
                cands = [(n, i) for n, i in self.intents.items()
                         if i["exige_ctx"] == self.contexto]
                if cands:
                    melhor = max(cands, key=lambda x: max(
                        (len(set(ml.split()) & set(f.split())) /
                         max(len(set(ml.split()) | set(f.split())), 1)
                         for f in x[1]["frases"]), default=0))[0]
                    score = 0.01
                else: melhor = None
            else: melhor = None
        if melhor:
            intent = self.intents[melhor]
            if intent["gera_ctx"] is not None: self.contexto = intent["gera_ctx"]
            ents = self._extrair(ml, intent["entidades"]); self.dados.update(ents)
            resp = random.choice(intent["respostas"])
            for k, v in {**self.dados, **ents}.items(): resp = resp.replace(f"{{{k}}}", str(v))
            if intent["acao"]:
                r2 = intent["acao"](ml, self.dados)
                if r2: resp = r2
        else:
            melhor, score, ents = "fallback", 0.0, {}
            resp = random.choice([
                "Nao entendi. Pode reformular a pergunta?",
                "Hmm, nao sei responder isso. Pode tentar de outro jeito?",
                "Nao captei! Tenta perguntar diferente.",
            ])
        return {"intent": melhor, "score": round(score, 2),
                "resposta": resp, "contexto": self.contexto}

    def _extrair(self, msg, defs):
        r = {}
        for d in defs:
            for v in d.get("valores", []):
                if v.lower() in msg: r[d["nome"]] = v; break
        return r

    def resetar(self): self.contexto = None; self.dados = {}

    def chat(self, debug=True):
        print(f"\n{Fore.CYAN}{'='*54}")
        print(f"  📚  Biblioteca Escolar — Atendimento Virtual")
        print(f"  'sair' = encerrar | 'reset' = nova conversa")
        print(f"{'='*54}{Style.RESET_ALL}\n")
        while True:
            try:
                user = input(f"{Fore.GREEN}Voce >>> {Style.RESET_ALL}").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not user: continue
            if user.lower() == "sair":
                print(f"\n{Fore.CYAN}  Ate mais! Bons estudos! 📖{Style.RESET_ALL}")
                break
            if user.lower() == "reset":
                self.resetar()
                print(f"{Fore.YELLOW}  [Nova conversa iniciada]{Style.RESET_ALL}\n")
                continue
            r = self.detectar(user)
            print(f"{Fore.BLUE}Bot  >>> {r['resposta']}{Style.RESET_ALL}")
            if debug:
                print(f"{Fore.WHITE}         [intent: {r['intent']} | "
                      f"certeza: {r['score']:.0%}]{Style.RESET_ALL}")
            print()


# ════════════════════════════════════════════════════════════
#  CONFIGURACAO DO BOT DA BIBLIOTECA
# ════════════════════════════════════════════════════════════

bot = MiniDialogflow("BibliotecaBot")

# INTENT 1: Saudacao e apresentacao
bot.treinar_intent(
    nome="saudacao",
    frases=["oi", "ola", "bom dia", "boa tarde", "boa noite",
            "hey", "eai", "ola biblioteca", "preciso de ajuda"],
    respostas=[
        "Ola! Bem-vindo a Biblioteca Escolar! 📚\n"
        "Posso te ajudar com:\n"
        "  • Horario de funcionamento\n"
        "  • Emprestimo de livros\n"
        "  • Prazo de devolucao\n"
        "  • Multa por atraso\n"
        "  • Clube do Livro\n"
        "O que voce precisa saber?",
    ]
)

# INTENT 2: Horario de funcionamento
bot.treinar_intent(
    nome="horario",
    frases=[
        "qual o horario", "que horas abre", "que horas fecha",
        "horario de funcionamento", "a biblioteca esta aberta",
        "quando posso ir", "horario da biblioteca",
        "funciona sabado", "abre fim de semana",
    ],
    respostas=[
        "🕐 Horario de funcionamento:\n\n"
        "  Segunda a Sexta: 7h30 as 17h00\n"
        "  Sabado          : 8h00 as 12h00\n"
        "  Domingo         : FECHADO\n\n"
        "Nos feriados tambem ficamos fechados!",
    ]
)

# INTENT 3: Como fazer emprestimo
bot.treinar_intent(
    nome="emprestimo",
    frases=[
        "como faz emprestimo", "quero pegar um livro",
        "como pego livro emprestado", "posso pegar livro",
        "como funciona o emprestimo", "preciso de livro",
        "como empresto um livro", "quero emprestar",
        "processo de emprestimo",
    ],
    respostas=[
        "📖 Como fazer o emprestimo:\n\n"
        "  1. Traga sua carteirinha de estudante\n"
        "  2. Escolha o(s) livro(s) desejado(s)\n"
        "  3. Va ao balcao e apresente a carteirinha\n\n"
        "Limite: 2 livros por vez\n"
        "Prazo : 7 dias (pode renovar 1 vez!)",
    ]
)

# INTENT 4: Prazo de devolucao e renovacao
bot.treinar_intent(
    nome="devolucao",
    frases=[
        "quando devolver", "prazo de devolucao", "quando devo devolver",
        "posso renovar", "como renovar", "quero renovar o livro",
        "extensao do prazo", "posso ficar mais tempo",
        "quantos dias posso ficar", "prazo",
    ],
    respostas=[
        "📅 Prazo e renovacao:\n\n"
        "  Prazo padrao: 7 dias corridos\n"
        "  Renovacao   : 1 vez (mais 7 dias)\n\n"
        "Para renovar, venha pessoalmente ao balcao\n"
        "OU mande mensagem aqui mesmo antes do vencimento!\n\n"
        "Importante: renovacao nao e permitida se ja\n"
        "estiver em atraso.",
    ]
)

# INTENT 5: Multa por atraso
bot.treinar_intent(
    nome="multa",
    frases=[
        "qual a multa", "quanto custa a multa", "multa por atraso",
        "quanto pago se atrasar", "esqueci de devolver",
        "devolvi atrasado", "quanto e a multa",
        "taxa de atraso", "penalidade",
    ],
    respostas=[
        "💰 Multa por atraso:\n\n"
        "  R$ 0,50 por dia de atraso por livro\n\n"
        "Exemplo: 3 dias de atraso com 2 livros\n"
        "         = 3 x R$0,50 x 2 = R$ 3,00\n\n"
        "O pagamento e feito na secretaria da escola.\n"
        "Enquanto houver pendencia, novos emprestimos\n"
        "ficam bloqueados.",
    ]
)

# INTENT 6: Clube do livro
bot.treinar_intent(
    nome="clube_do_livro",
    frases=[
        "clube do livro", "evento literario", "o que tem na biblioteca",
        "tem algum evento", "quero participar do clube",
        "quando e o clube", "horario do clube",
        "como entrar no clube", "atividades da biblioteca",
    ],
    respostas=[
        "📖✨ Clube do Livro:\n\n"
        "  Quando : Toda terca-feira\n"
        "  Horario: 15h00 as 16h30\n"
        "  Local  : Sala de leitura (Biblioteca)\n\n"
        "E gratuito e aberto a todos os alunos!\n"
        "Nao precisa se inscrever, e so aparecer.\n"
        "Este mes estamos lendo: '1984' de George Orwell.",
    ]
)

# INTENT 7: Despedida
bot.treinar_intent(
    nome="despedida",
    frases=["tchau", "ate mais", "ate logo", "obrigado", "valeu",
            "ja sei", "consegui", "ajudou", "obrigada"],
    respostas=[
        "De nada! Bons estudos! 📚",
        "Ate mais! Qualquer duvida e so perguntar!",
        "Disponha! A biblioteca esta sempre aqui pra voce!",
    ]
)


# ════════════════════════════════════════════════════════════
#  DEMONSTRACAO AUTOMATICA
# ════════════════════════════════════════════════════════════

print(f"\n{Fore.YELLOW}{'='*54}")
print("  EXERCICIO 1 — Bot da Biblioteca Escolar")
print("  Demonstracao de perguntas frequentes")
print(f"{'='*54}{Style.RESET_ALL}\n")

perguntas_demo = [
    "oi, preciso de ajuda",
    "que horas a biblioteca abre",
    "como faco para pegar um livro emprestado",
    "quanto tempo tenho para devolver",
    "e se eu atrasar a devolucao",
    "tem alguma atividade especial",
]

for pergunta in perguntas_demo:
    r = bot.detectar(pergunta)
    print(f"  Aluno: {Fore.GREEN}{pergunta}{Style.RESET_ALL}")
    print(f"  Bot  : {Fore.BLUE}{r['resposta'][:80]}{'...' if len(r['resposta'])>80 else ''}{Style.RESET_ALL}")
    print(f"         [{r['intent']} | {r['score']:.0%}]\n")

print(f"{Fore.CYAN}{'='*54}")
print("  Demonstracao concluida!")
print(f"{'='*54}{Style.RESET_ALL}")


# ════════════════════════════════════════════════════════════
#  PONTO DE ENTRADA — F5 / ▶ abre o chat interativo
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print()
    bot.chat()
