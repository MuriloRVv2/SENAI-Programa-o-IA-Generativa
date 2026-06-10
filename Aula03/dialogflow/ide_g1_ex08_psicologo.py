# ╔══════════════════════════════════════════════════════════╗
# ║  💙  Bot com Analise de Sentimento                 ║
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
#     Detecta se o usuario esta feliz, triste ou neutro e adapta
#     o estilo da resposta de acordo com o humor!
#  
#  Conceito ensinado — ANALISE DE SENTIMENTO:
#     O Dialogflow real consegue analisar o "tom" de uma mensagem.
#     Aqui implementamos uma versao simplificada com palavras-chave.
#     Respostas positivas recebem celebracao; negativas recebem empatia!
#  
#  Conceito ensinado — ESCALADA DE CRISE:
#     Bots de saude mental SEMPRE devem detectar sinais de crise e
#     oferecer recursos de apoio imediatamente. Isso e uma responsabilidade!
#  
#  Pense assim:
#     e como um amigo que percebe quando voce esta mal sem voce precisar
#     dizer explicitamente. Ele muda o tom da conversa automaticamente.
#  
#     NOTA IMPORTANTE: Este bot e apenas didatico. Para suporte real,
#     sempre indique profissionais de saude mental!
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
#  2. Digite: python g1_ex08_psicologo.py
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

# Dicionarios de palavras-chave para cada sentimento
POSITIVAS = {"otimo", "incrivel", "adorei", "feliz", "perfeito", "amei",
             "satisfeito", "excelente", "maravilha", "passei", "aprovado",
             "consegui", "alegre", "contente"}
NEGATIVAS  = {"ruim", "pessimo", "horrivel", "triste", "chateado",
              "frustrado", "insatisfeito", "raiva", "reprovado",
              "dificil", "sofrendo", "cansado", "ansioso", "mal"}
CRISE      = {"suicidio", "me matar", "quero morrer",
              "nao quero mais viver", "sem saida"}

def detectar_sentimento(msg):
    """Detecta o sentimento da mensagem por palavras-chave."""
    palavras = set(msg.lower().split())
    if any(c in msg.lower() for c in CRISE):
        return "crise"
    if palavras & POSITIVAS:
        return "positivo"
    if palavras & NEGATIVAS:
        return "negativo"
    return "neutro"

def resposta_por_sentimento(msg, dados):
    """Retorna uma resposta diferente de acordo com o sentimento."""
    sent = detectar_sentimento(msg)
    if sent == "crise":
        return ("Percebi que voce pode estar passando por algo muito dificil.\n\n"
                "Por favor, entre em contato agora:\n"
                "📞 CVV: 188 (24h, gratis, sigiloso)\n"
                "💬 cvv.org.br\n"
                "🏥 SAMU: 192\n\n"
                "Voce nao esta sozinho(a). Ha pessoas que se importam com voce.")
    resps = {
        "positivo": ["Que legal! Fico muito feliz por voce! 🎉 Me conta mais?",
                     "Que otimo! Continue assim! 😊"],
        "negativo": ["Sinto muito que esta assim.\nQuer me contar o que aconteceu?",
                     "Entendo. Isso soa dificil. Estou aqui para ouvir!"],
        "neutro"  : ["Entendo! Como posso te ajudar hoje?",
                     "Ok! Tem algo que eu possa fazer por voce?"],
    }
    return random.choice(resps.get(sent, resps["neutro"]))

bot = MiniDialogflow("MindBot")

bot.treinar_intent(
    nome="como_vai",
    frases=["tudo bem", "como vai", "estou bem", "estou mal",
            "mais ou menos", "pessimo", "otimo", "ta bom"],
    respostas=["Me conta mais sobre como voce esta se sentindo."],
    acao=resposta_por_sentimento
)

bot.treinar_intent(
    nome="desabafo",
    frases=["estou triste", "me sinto mal", "to deprimido",
            "ansioso", "passei na prova", "consegui o emprego",
            "estou muito feliz", "foi um dia ruim"],
    respostas=["Obrigado por compartilhar."],
    acao=resposta_por_sentimento
)

bot.treinar_intent(
    nome="recursos",
    frases=["preciso de ajuda", "apoio psicologico", "onde buscar ajuda",
            "recursos de saude mental", "preciso de psicologo"],
    respostas=["Recursos de saude mental gratuitos:\n\n"
               "📞 CVV: 188 (24h, gratis)\n"
               "💬 cvv.org.br (chat)\n"
               "🏥 CAPS: Centro de Atencao Psicossocial\n"
               "🌐 saude.gov.br/saude-mental"]
)

# ════════════════════════════════════════════════════════════
#  TESTES AUTOMATICOS (rodam ao executar o arquivo)
# ════════════════════════════════════════════════════════════

print(f"\n{Fore.YELLOW}{'='*50}")
print("  TESTANDO ANALISE DE SENTIMENTO")
print(f"{'='*50}{Style.RESET_ALL}\n")

testes = [
    ("passei no vestibular estou muito feliz!", "positivo"),
    ("estou muito triste hoje",                 "negativo"),
    ("mais ou menos, ta indo",                  "neutro"),
]
for msg, sent_esperado in testes:
    sent_real = detectar_sentimento(msg)
    r = bot.detectar(msg)
    ok = sent_real == sent_esperado
    print(f"  {'✓' if ok else '✗'} Sentimento: {sent_real} (esperado: {sent_esperado})")
    print(f"    Msg: '{msg}'")
    print(f"    Bot: '{r['resposta'][:70]}'\n")

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
