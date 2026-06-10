# ╔══════════════════════════════════════════════════════════╗
# ║  🎯  Bot Adivinha com Dicas e Dificuldades         ║
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
#     Versao avancada do jogo de adivinhar com 3 dificuldades (facil/normal/dificil),
#     dicas de temperatura (GELADO / MORNO / QUENTE / QUEIMANDO!)
#     e historico de chutes para nao repetir.
#  
#  Como e diferente do Grupo 1:
#     G1: so dizia "maior" ou "menor".
#     G2: da dicas de temperatura, 3 modos de dificuldade, max de tentativas
#     e uma dica de paridade (par/impar) a cada 3 tentativas!
#  
#  Dica de estudo:
#     Veja como o dicionario 'estado' guarda informacoes durante o jogo.
#     Em sistemas reais isso e chamado de "session state" — dados que
#     persistem durante toda a sessao do usuario!
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
#  2. Digite: python g2_ex03_adivinha_turbinado.py
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

LIMITES = {"facil": 20, "normal": 50, "dificil": 100}
MAX_TENT = {"facil": 15, "normal": 10, "dificil": 7}

# Estado do jogo (dicionario global)
estado = {
    "numero"     : None,
    "tentativas" : 0,
    "max"        : 10,
    "chutes"     : [],
    "rodando"    : False,
    "dificuldade": "normal",
}

def nova_partida(msg, dados):
    dif = "normal"
    if "facil"   in msg: dif = "facil"
    if "dificil" in msg: dif = "dificil"
    lim = LIMITES[dif]
    estado.update({
        "numero"     : random.randint(1, lim),
        "tentativas" : 0,
        "max"        : MAX_TENT[dif],
        "chutes"     : [],
        "rodando"    : True,
        "dificuldade": dif,
    })
    return (f"Modo {dif.upper()} iniciado! 🎮\n"
            f"Numero de 1 a {lim} | {estado['max']} tentativas. Vai la!")

def processar_chute(msg, dados):
    if not estado["rodando"]:
        return "Diz 'quero jogar' para comecar!"
    nums = re.findall(r"\d+", msg)
    if not nums:
        return "Fala um numero!"
    chute = int(nums[0])
    lim   = LIMITES[estado["dificuldade"]]
    if not (1 <= chute <= lim):
        return f"Numero deve estar entre 1 e {lim}!"
    if chute in estado["chutes"]:
        return f"Voce ja tentou {chute}! Nao vale repetir."
    estado["tentativas"] += 1
    estado["chutes"].append(chute)
    restantes = estado["max"] - estado["tentativas"]
    if chute == estado["numero"]:
        t = estado["tentativas"]
        estado["rodando"] = False
        nota = ("PERFEITO! 🏆" if t <= 3 else
                "Muito bom! 🥇" if t <= 6 else "Conseguiu! 👍")
        return (f"ACERTOU!! Era o {chute}! {nota}\n"
                f"Usou {t} tentativas.\n"
                f"Quer jogar de novo? Diz 'quero jogar'!")
    # Calcula a "temperatura" baseada na distancia
    diff = abs(chute - estado["numero"])
    if diff <= 2:   temp = "QUEIMANDO 🔥🔥🔥"
    elif diff <= 5: temp = "Muito quente ♨️"
    elif diff <= 10:temp = "Quente 🌡"
    elif diff <= 20:temp = "Morno 😐"
    else:           temp = "Gelado ❄️"
    direcao = "MAIOR" if chute < estado["numero"] else "MENOR"
    msg_r = f"{temp}! O numero e {direcao} que {chute}.\nTentativas restantes: {restantes}"
    if restantes == 0:
        estado["rodando"] = False
        msg_r += f"\n\nFim de jogo! Era {estado['numero']}. Quer tentar de novo?"
    elif estado["tentativas"] % 3 == 0:
        par = "par" if estado["numero"] % 2 == 0 else "impar"
        msg_r += f"\n💡 Dica: o numero e {par}!"
    return msg_r

bot = MiniDialogflow("AdivinhaBot")

bot.treinar_intent(
    nome="iniciar",
    frases=["quero jogar", "jogar", "comecar", "bora", "novo jogo",
            "de novo", "modo facil", "modo dificil", "facil", "dificil"],
    respostas=["Iniciando..."],
    gera_ctx="jogando",
    acao=nova_partida
)

bot.treinar_intent(
    nome="chute",
    frases=["meu chute", "acho que e", "tento", "numero",
            "e o", "1", "5", "10", "20", "50"],
    respostas=["Verificando..."],
    exige_ctx="jogando",
    acao=processar_chute
)

bot.treinar_intent(
    nome="historico",
    frases=["quais tentei", "meus chutes", "historico de chutes"],
    respostas=["Verificando historico..."],
    exige_ctx="jogando",
    acao=lambda m, d: (f"Seus chutes: {estado['chutes']}"
                       if estado["chutes"] else "Nenhum chute ainda!")
)

bot.treinar_intent(
    nome="desistir",
    frases=["desisto", "me da a resposta", "qual e o numero", "nao sei"],
    respostas=["Processando..."],
    exige_ctx="jogando",
    acao=lambda m, d: (
        f"Era o {estado['numero']}! Quer jogar de novo?"
        if estado["rodando"] else "Jogo nao ativo!"
    )
)

# ════════════════════════════════════════════════════════════
#  TESTES AUTOMATICOS (rodam ao executar o arquivo)
# ════════════════════════════════════════════════════════════

print(f"\n{Fore.YELLOW}{'='*50}")
print("  SIMULANDO PARTIDA COM DICAS DE TEMPERATURA")
print(f"{'='*50}{Style.RESET_ALL}\n")

# Inicia o jogo
r = bot.detectar("quero jogar modo facil")
print(f"  Voce: 'quero jogar modo facil'")
print(f"  Bot : '{r['resposta']}'\n")

# Simula alguns chutes
for chute in ["10", "5", "15", str(estado.get("numero") or 7)]:
    r = bot.detectar(chute)
    print(f"  Voce: '{chute}' | Numero secreto: {estado.get('numero')}")
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
