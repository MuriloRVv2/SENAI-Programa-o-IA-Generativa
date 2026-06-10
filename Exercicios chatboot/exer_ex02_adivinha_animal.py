# ╔══════════════════════════════════════════════════════════╗
# ║  🐾  EXERCICIO 2 — Bot Adivinhe o Animal               ║
# ║  Nivel: Medio  |  Base: Exemplo 03 (Adivinha)          ║
# ╚══════════════════════════════════════════════════════════╝
#
# ════════════════════════════════════════════════════════════
#  GABARITO — resultado esperado apos o uso do prompt
# ════════════════════════════════════════════════════════════
#
# CONTEXTO DO EXERCICIO:
#   Voce trabalha na area de jogos educativos de uma escola.
#   O professor de Ciencias pediu um jogo interativo onde
#   os alunos pratiquem perguntas de SIM/NAO para descobrir
#   um animal que o bot esta "pensando".
#
# O QUE O BOT DEVE FAZER:
#   - Sortear um animal de uma lista
#   - Responder SIM/NAO para perguntas sobre o animal
#   - Aceitar o chute do aluno (acertou ou errou?)
#   - Contar quantas perguntas foram feitas
#   - Dar dica automatica a cada 3 perguntas
#   - Limitar a 10 perguntas por partida
#
# PROMPT QUE GEROU ESTE CODIGO:
#   "Crie um chatbot em Python com a classe MiniDialogflow
#    para o jogo 'Adivinhe o Animal'. O bot sorteia um animal
#    de uma lista de 10: cachorro, gato, leao, elefante, peixe,
#    passaro, cobra, coelho, macaco, tartaruga.
#    O usuario faz perguntas de sim/nao como:
#    'tem 4 patas?', 'e grande?', 'vive na agua?', 'e domestico?'
#    O bot responde com base em um dicionario de caracteristicas
#    de cada animal. O usuario pode tentar adivinhar dizendo
#    'e um [animal]'. Limite de 10 perguntas. A cada 3 perguntas
#    o bot da uma dica extra. Use contexto para controlar o estado
#    do jogo. Inclua a classe completa e chame bot.chat()."
#
# INSTALACAO: pip install colorama
# COMO RODAR: python ex02_adivinha_animal.py
# ════════════════════════════════════════════════════════════

import re
import random
from colorama import Fore, Style, init
init(autoreset=True)


class MiniDialogflow:
    """Simula o Dialogflow — versao com context-aware fallback."""

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
                "Nao entendi. Tenta formular a pergunta como SIM/NAO!",
                "Pergunta assim: 'tem 4 patas?' ou 'e grande?'",
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
        print(f"  🐾  Adivinhe o Animal — Bot Educativo")
        print(f"  'sair' = encerrar | 'reset' = novo jogo")
        print(f"{'='*54}{Style.RESET_ALL}\n")
        while True:
            try:
                user = input(f"{Fore.GREEN}Voce >>> {Style.RESET_ALL}").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not user: continue
            if user.lower() == "sair":
                print(f"\n{Fore.CYAN}  Ate mais! 🐾{Style.RESET_ALL}")
                break
            if user.lower() == "reset":
                self.resetar(); estado.update(ESTADO_INICIAL.copy())
                print(f"{Fore.YELLOW}  [Novo jogo iniciado!]{Style.RESET_ALL}\n")
                continue
            r = self.detectar(user)
            print(f"{Fore.BLUE}Bot  >>> {r['resposta']}{Style.RESET_ALL}")
            if debug:
                print(f"{Fore.WHITE}         [intent: {r['intent']} | "
                      f"certeza: {r['score']:.0%}]{Style.RESET_ALL}")
            print()


# ════════════════════════════════════════════════════════════
#  BANCO DE ANIMAIS COM CARACTERISTICAS
# ════════════════════════════════════════════════════════════
# Cada animal tem um dicionario de atributos para responder SIM/NAO

ANIMAIS = {
    "cachorro" : {"patas":True,"grande":False,"agua":False,"domestico":True,
                  "pelo":True,"ovo":False,"voa":False,"carnivoro":True,
                  "dica":"Melhor amigo do homem!"},
    "gato"     : {"patas":True,"grande":False,"agua":False,"domestico":True,
                  "pelo":True,"ovo":False,"voa":False,"carnivoro":True,
                  "dica":"Mia e ronrona!"},
    "leao"     : {"patas":True,"grande":True,"agua":False,"domestico":False,
                  "pelo":True,"ovo":False,"voa":False,"carnivoro":True,
                  "dica":"Rei da selva!"},
    "elefante" : {"patas":True,"grande":True,"agua":False,"domestico":False,
                  "pelo":False,"ovo":False,"voa":False,"carnivoro":False,
                  "dica":"Maior animal terrestre!"},
    "peixe"    : {"patas":False,"grande":False,"agua":True,"domestico":True,
                  "pelo":False,"ovo":True,"voa":False,"carnivoro":True,
                  "dica":"Respira com brânquias!"},
    "passaro"  : {"patas":False,"grande":False,"agua":False,"domestico":True,
                  "pelo":False,"ovo":True,"voa":True,"carnivoro":False,
                  "dica":"Canta de manha!"},
    "cobra"    : {"patas":False,"grande":False,"agua":False,"domestico":False,
                  "pelo":False,"ovo":True,"voa":False,"carnivoro":True,
                  "dica":"Reptil sem pernas!"},
    "coelho"   : {"patas":True,"grande":False,"agua":False,"domestico":True,
                  "pelo":True,"ovo":False,"voa":False,"carnivoro":False,
                  "dica":"Famoso pelas orelhas grandes!"},
    "macaco"   : {"patas":True,"grande":False,"agua":False,"domestico":False,
                  "pelo":True,"ovo":False,"voa":False,"carnivoro":False,
                  "dica":"Nosso primo mais proximo!"},
    "tartaruga": {"patas":True,"grande":False,"agua":True,"domestico":True,
                  "pelo":False,"ovo":True,"voa":False,"carnivoro":False,
                  "dica":"Animal muito longo!"},
}

NOMES_ANIMAIS = list(ANIMAIS.keys())

ESTADO_INICIAL = {
    "animal"   : None,
    "perguntas": 0,
    "max_pergs": 10,
    "rodando"  : False,
}
estado = ESTADO_INICIAL.copy()


# ════════════════════════════════════════════════════════════
#  FUNCOES DO JOGO (Fulfillment)
# ════════════════════════════════════════════════════════════

def iniciar_jogo(msg, dados):
    """Sorteia um animal e inicia a partida."""
    animal = random.choice(NOMES_ANIMAIS)
    estado.update({
        "animal"   : animal,
        "perguntas": 0,
        "rodando"  : True,
    })
    print(f"  {Fore.WHITE}[DEBUG professor: animal = {animal}]{Style.RESET_ALL}")
    return (f"Jogo iniciado! 🐾 Pensei num animal.\n\n"
            f"Voce tem {estado['max_pergs']} perguntas de SIM/NAO.\n"
            f"Exemplos de perguntas:\n"
            f"  'tem 4 patas?' | 'e grande?' | 'vive na agua?'\n"
            f"  'e domestico?' | 'tem pelo?' | 'bota ovo?' | 'voa?'\n\n"
            f"Pode tentar adivinhar a qualquer momento:\n"
            f"  'e um cachorro?' | 'sera que e um gato?'\n\n"
            f"Pergunta 1/{estado['max_pergs']}: vai la!")


def responder_pergunta(msg, dados):
    """Responde SIM/NAO com base nas caracteristicas do animal."""
    if not estado["rodando"]:
        return "Diz 'quero jogar' para comecar um novo jogo!"

    animal    = estado["animal"]
    atributos = ANIMAIS[animal]

    # Mapeia palavras-chave para atributos
    MAPA = {
        "patas"    : ["pata", "pernas", "4 patas", "quatro patas"],
        "grande"   : ["grande", "grande porte", "gigante", "enorme"],
        "agua"     : ["agua", "aquatico", "nadar", "vive na agua", "mar"],
        "domestico": ["domestico", "animal de estimacao", "de casa", "pet"],
        "pelo"     : ["pelo", "peludo", "pelagem", "cabelo"],
        "ovo"      : ["ovo", "bota ovo", "choca", "oviparo"],
        "voa"      : ["voa", "voar", "asa", "voa alto"],
        "carnivoro": ["carnivoro", "come carne", "predador", "carnivora"],
    }

    atributo_perguntado = None
    for atrib, palavras in MAPA.items():
        if any(p in msg for p in palavras):
            atributo_perguntado = atrib
            break

    if atributo_perguntado is None:
        return ("Nao entendi a pergunta!\n"
                "Tenta assim: 'tem 4 patas?', 'e grande?', 'vive na agua?'")

    estado["perguntas"] += 1
    restantes = estado["max_pergs"] - estado["perguntas"]
    resposta  = "SIM! ✅" if atributos[atributo_perguntado] else "NAO! ❌"

    msg_r = f"{resposta}\n  Perguntas restantes: {restantes}"

    # Dica a cada 3 perguntas
    if estado["perguntas"] % 3 == 0 and restantes > 0:
        msg_r += f"\n\n💡 Dica extra: {atributos['dica']}"

    # Sem mais perguntas
    if restantes == 0:
        estado["rodando"] = False
        msg_r += (f"\n\n⏰ Acabaram as perguntas! O animal era: {animal.upper()}!\n"
                  f"Quer jogar de novo? Diz 'quero jogar'!")

    return msg_r


def verificar_chute(msg, dados):
    """Verifica se o aluno adivinhou o animal."""
    if not estado["rodando"]:
        return "Diz 'quero jogar' para comecar um novo jogo!"

    animal = estado["animal"]
    # Verifica se o nome do animal aparece no chute
    for nome in NOMES_ANIMAIS:
        if nome in msg:
            if nome == animal:
                pergs = estado["perguntas"]
                estado["rodando"] = False
                return (f"PARABENS! 🎉 Era mesmo um {animal.upper()}!\n"
                        f"Voce usou {pergs} perguntas para descobrir!\n"
                        f"Quer jogar de novo? Diz 'quero jogar'!")
            else:
                estado["perguntas"] += 1
                restantes = estado["max_pergs"] - estado["perguntas"]
                if restantes <= 0:
                    estado["rodando"] = False
                    return (f"NAO era um {nome}. ❌\n"
                            f"Acabaram as chances! Era um {animal.upper()}!\n"
                            f"Diz 'quero jogar' para nova partida!")
                return (f"NAO era um {nome}. ❌ Continua tentando!\n"
                        f"Perguntas restantes: {restantes}")
    return "Qual animal voce acha que e? Diz 'e um [animal]'"


def ver_animais(msg, dados):
    """Mostra a lista de animais possiveis."""
    return f"Animais possiveis:\n{', '.join(NOMES_ANIMAIS)}"


# ════════════════════════════════════════════════════════════
#  CONFIGURACAO DO BOT
# ════════════════════════════════════════════════════════════

bot = MiniDialogflow("AdivinhaAnimalBot")

bot.treinar_intent(
    nome="iniciar",
    frases=["quero jogar", "vamos jogar", "comecar", "novo jogo",
            "jogar", "bora", "iniciar", "de novo", "outra rodada"],
    respostas=["Iniciando jogo..."],
    gera_ctx="jogando", acao=iniciar_jogo
)

bot.treinar_intent(
    nome="pergunta_sim_nao",
    frases=["tem 4 patas", "e grande", "vive na agua", "e domestico",
            "tem pelo", "bota ovo", "voa", "e carnivoro",
            "tem patas", "e pequeno", "aquatico", "animal de estimacao",
            "e peludo", "choca ovo", "tem asa", "come carne"],
    respostas=["Verificando..."],
    exige_ctx="jogando", acao=responder_pergunta
)

bot.treinar_intent(
    nome="tentar_adivinhar",
    frases=["e um", "sera que e", "e o", "aposto que e", "acho que e",
            "cachorro", "gato", "leao", "elefante", "peixe",
            "passaro", "cobra", "coelho", "macaco", "tartaruga"],
    respostas=["Verificando chute..."],
    exige_ctx="jogando", acao=verificar_chute
)

bot.treinar_intent(
    nome="ver_lista",
    frases=["quais animais", "lista de animais", "que animais pode ser",
            "opcoes", "animais possiveis"],
    respostas=["Mostrando lista..."],
    acao=ver_animais
)

bot.treinar_intent(
    nome="desistir",
    frases=["desisto", "me da a resposta", "qual e o animal",
            "nao sei", "revela", "qual era"],
    respostas=["..."],
    exige_ctx="jogando",
    acao=lambda m, d: (
        f"Era um {estado['animal'].upper()}! 🐾\n"
        f"Quer tentar de novo? Diz 'quero jogar'!"
        if estado["rodando"] else "Nenhum jogo ativo!"
    )
)


# ════════════════════════════════════════════════════════════
#  DEMONSTRACAO AUTOMATICA
# ════════════════════════════════════════════════════════════

print(f"\n{Fore.YELLOW}{'='*54}")
print("  EXERCICIO 2 — Bot Adivinhe o Animal")
print("  Demonstracao de uma rodada")
print(f"{'='*54}{Style.RESET_ALL}\n")

demo_msgs = [
    "quero jogar",
    "tem 4 patas",
    "e domestico",
    "tem pelo",
    "e um cachorro",
]

for msg in demo_msgs:
    r = bot.detectar(msg)
    print(f"  Aluno: {Fore.GREEN}{msg}{Style.RESET_ALL}")
    print(f"  Bot  : {Fore.BLUE}{r['resposta'][:90]}{'...' if len(r['resposta'])>90 else ''}{Style.RESET_ALL}\n")

# Reset para o chat interativo
bot.resetar()
estado.update(ESTADO_INICIAL.copy())

print(f"{Fore.CYAN}{'='*54}")
print("  Demonstracao concluida! Agora e sua vez.")
print(f"{'='*54}{Style.RESET_ALL}")


# ════════════════════════════════════════════════════════════
#  PONTO DE ENTRADA — F5 / ▶ abre o chat
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print()
    bot.chat()
