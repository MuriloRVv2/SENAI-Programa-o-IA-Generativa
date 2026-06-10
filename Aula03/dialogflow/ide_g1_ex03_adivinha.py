# ╔══════════════════════════════════════════════════════════╗
# ║  🎮  Bot Adivinha o Numero                         ║
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
#     Um jogo de adivinhar um numero de 1 a 20!
#     O bot pensa num numero e da dicas (maior ou menor) a cada chute.
#  
#  Conceito ensinado — FULFILLMENT:
#     Fulfillment e quando o bot executa um codigo Python real ao detectar
#     um intent, em vez de so retornar texto fixo.
#     Aqui, ao receber um chute, o bot CALCULA: acertou? foi alto? foi baixo?
#  
#  Conceito ensinado — CONTEXTO:
#     O contexto e a "memoria" da conversa. So apos dizer "quero jogar"
#     o contexto muda para "jogando" — e so entao o bot aceita os chutes!
#  
#  Pense assim:
#     e como uma fila de supermercado: voce precisa pegar a senha (iniciar o
#     jogo) antes de ser atendido. Sem a senha, o caixa te ignora!
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
#  2. Digite: python g1_ex03_adivinha.py
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

# Estado do jogo — guardado em uma lista para poder modificar dentro das funcoes
numero_secreto = [random.randint(1, 20)]
tentativas     = [0]

# ── Funcao do Fulfillment ──────────────────────────────────────
# Esta funcao e chamada automaticamente quando o intent "dar_chute" e detectado
def processar_chute(msg, dados):
    """Recebe a mensagem, extrai o numero e verifica se acertou."""
    nums = re.findall(r"\d+", msg)
    if not nums:
        return "Fala um numero de 1 a 20! (ex: 'meu chute e 10')"
    chute = int(nums[0])
    if not (1 <= chute <= 20):
        return "O numero tem que estar entre 1 e 20!"
    tentativas[0] += 1
    if chute == numero_secreto[0]:
        t = tentativas[0]
        tentativas[0] = 0  # reseta para o proximo jogo
        return (f"ACERTOU!! Era o {chute}! 🎉\n"
                f"{'PERFEITO!' if t<=3 else 'Muito bom!' if t<=6 else 'Conseguiu!'}"
                f" ({t} tentativas)\n\nQuer jogar de novo? Diz 'quero jogar'!")
    direcao = "MAIOR" if chute < numero_secreto[0] else "MENOR"
    return f"Errou! O numero e {direcao} que {chute}. Tentativa {tentativas[0]}/?"

# ── Configuracao do bot ────────────────────────────────────────
bot = MiniDialogflow("AdivinhaBot")

# Iniciar o jogo — gera_ctx="jogando" ativa o contexto
bot.treinar_intent(
    nome="iniciar_jogo",
    frases=["quero jogar", "vamos jogar", "comecar", "jogar",
            "bora jogar", "novo jogo", "de novo", "iniciar"],
    respostas=[f"Pensei num numero de 1 a 20. Qual e seu chute?"],
    gera_ctx="jogando"  # ← ativa o contexto "jogando"
)

# Dar um chute — exige_ctx="jogando" so funciona quando o jogo esta ativo
bot.treinar_intent(
    nome="dar_chute",
    frases=["meu chute e", "acho que e", "tento o",
            "numero", "e o", "chuto", "1", "5", "10", "15", "20"],
    respostas=["Calculando..."],
    exige_ctx="jogando",  # ← so funciona quando contexto = "jogando"
    acao=processar_chute  # ← chama a funcao acima
)

# Desistir
bot.treinar_intent(
    nome="desistir",
    frases=["desisto", "me da a resposta", "qual e", "revela", "nao sei"],
    respostas=[f"Desistiu! Era o {numero_secreto[0]}. Quer jogar de novo?"],
    exige_ctx="jogando"
)

# ════════════════════════════════════════════════════════════
#  TESTES AUTOMATICOS (rodam ao executar o arquivo)
# ════════════════════════════════════════════════════════════

print(f"\n{Fore.YELLOW}{'='*50}")
print("  SIMULANDO UMA PARTIDA")
print(f"  (Numero secreto: {numero_secreto[0]})")
print(f"{'='*50}{Style.RESET_ALL}\n")

for msg in ["quero jogar", "10", "15", str(numero_secreto[0])]:
    r = bot.detectar(msg)
    print(f"  Voce: '{msg}'")
    print(f"  Bot : '{r['resposta']}'\n")

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
