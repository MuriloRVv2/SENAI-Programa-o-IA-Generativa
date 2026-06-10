# ╔══════════════════════════════════════════════════════════╗
# ║  💬  Bot Bate-Papo Casual com Personalidade        ║
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
#     Um bot com personalidade propria que tem opinioes sobre filmes, musica,
#     jogos, comida, esporte, tecnologia, series e hobbies.
#  
#  Conceito ensinado — BOT com PERSONALIDADE:
#     Chatbots profissionais tem um "tom" e "estilo" consistentes.
#     Definir a personalidade do bot e parte essencial do design!
#     Aqui o bot tem gostos proprios e os compartilha naturalmente.
#  
#  Pense assim:
#     e como conversar com um novo amigo. Ele tem opiniao sobre filmes
#     e times de futebol, isso torna a conversa mais interessante
#     do que respostas roboticas e sem vida!
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
#  2. Digite: python g2_ex05_bate_papo.py
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

bot = MiniDialogflow("CasualBot")

bot.treinar_intent(
    nome="filmes",
    frases=["gosta de filme", "filme favorito", "voce assiste filme",
            "recomenda um filme", "que filme assistir"],
    respostas=["Adoro cinema! 🎬 Top 5: Matrix, Interestelar, Coringa, O Poderoso Chefao, Homem-Aranha!",
               "Interestelar e obra de arte! Mistura ciencia com emocao. Recomendo muito!"]
)

bot.treinar_intent(
    nome="musica",
    frases=["gosta de musica", "estilo de musica", "ouve musica",
            "artista favorito", "banda favorita"],
    respostas=["Curto de tudo! Trap, funk, lo-fi e os meus preferidos. E voce?",
               "Musica instrumental pra trabalhar e trap pra animar! Boa combinacao!"]
)

bot.treinar_intent(
    nome="comida",
    frases=["comida favorita", "prato favorito", "gosta de comer",
            "melhor comida", "o que comeria"],
    respostas=["Pizza de calabresa com borda recheada — perfeicao! 🍕",
               "Hamburguer artesanal com fritas seria minha escolha! 🍔"]
)

bot.treinar_intent(
    nome="jogos",
    frases=["joga videogame", "jogo favorito", "qual jogo voce joga",
            "playstation xbox", "pc ou console"],
    respostas=["PC sempre! CS2, Minecraft e Valorant dominam! 💻",
               "God of War e Red Dead 2 sao obras de arte! E vc, joga?"]
)

bot.treinar_intent(
    nome="esporte",
    frases=["gosta de esporte", "time de futebol", "esporte favorito",
            "assiste futebol", "copa do mundo"],
    respostas=["Futebol, basquete e F1 sao os que mais acompanho! 🏆"]
)

bot.treinar_intent(
    nome="tecnologia",
    frases=["iphone ou android", "apple ou samsung", "qual celular",
            "pc ou mac", "windows ou linux"],
    respostas=["Android! Mais liberdade e custo-beneficio! 🤖",
               "O melhor e o que voce sabe usar bem! Ferramenta e ferramenta!"]
)

bot.treinar_intent(
    nome="serie",
    frases=["serie favorita", "assiste serie", "recomenda serie",
            "netflix", "hbo", "o que assistir"],
    respostas=["Breaking Bad e o patamar mais alto! Depois Dark e The Last of Us! 📺",
               "Severance e Arcane estao no meu top recente. Muito bons!"]
)

bot.treinar_intent(
    nome="hobby",
    frases=["o que voce faz", "tem hobby", "passatempo", "tempo livre",
            "como se diverte"],
    respostas=["Aprendo coisas novas! Programacao, IA, filosofia... 🧠",
               "Ler, ouvir musica e conversar com pessoas — meu proposito!"]
)

# ════════════════════════════════════════════════════════════
#  TESTES AUTOMATICOS (rodam ao executar o arquivo)
# ════════════════════════════════════════════════════════════

print(f"\n{Fore.YELLOW}{'='*50}")
print("  CONVERSANDO CASUALMENTE")
print(f"{'='*50}{Style.RESET_ALL}\n")

for msg in ["qual seu filme favorito", "gosta de musica",
            "joga videogame", "iphone ou android", "serie favorita"]:
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
