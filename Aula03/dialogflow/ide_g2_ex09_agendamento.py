# ╔══════════════════════════════════════════════════════════╗
# ║  📅  Bot de Agendamento Medico                     ║
# ║  Nivel: Intermediario                                    ║
# ║  Ambiente: PyCharm / VSCode / Terminal                  ║
# ╚══════════════════════════════════════════════════════════╝
#
# ════════════════════════════════════════════════════════════
#  OLA, ALUNO! 👋  LEIA ANTES DE RODAR
# ════════════════════════════════════════════════════════════
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
#  2. Digite: python g2_ex09_agendamento.py
#  3. Pronto!
#
#  INSTALACAO (so na primeira vez — no terminal do projeto):
#    pip install pip install colorama scikit-learn
#
#  DURANTE O CHAT:
#    sair  → encerra o chat
#    reset → comeca uma nova conversa
# ════════════════════════════════════════════════════════════

import re
import math
import random
from datetime import datetime, timedelta
from colorama import Fore, Style, init
init(autoreset=True)


class MiniDialogflowPro:
    """Dialogflow aprimorado com TF-IDF + context-aware fallback."""

    def __init__(self, nome: str):
        self.nome = nome; self.intents = {}
        self.contexto = None; self.dados = {}; self._idf = {}

    def treinar_intent(self, nome, frases, respostas,
                       entidades=None, exige_ctx=None,
                       gera_ctx=None, acao=None):
        self.intents[nome] = {
            "frases": [f.lower().strip() for f in frases],
            "respostas": respostas, "entidades": entidades or [],
            "exige_ctx": exige_ctx, "gera_ctx": gera_ctx, "acao": acao,
        }
        self._recalcular_idf()

    def _tok(self, t): return re.findall(r"[a-z0-9]+", t.lower())

    def _recalcular_idf(self):
        docs = [set(self._tok(f)) for i in self.intents.values() for f in i["frases"]]
        if not docs: return
        N = len(docs); freq = {}
        for d in docs:
            for p in d: freq[p] = freq.get(p, 0) + 1
        self._idf = {p: math.log(N / (c + 1)) for p, c in freq.items()}

    def _tfidf(self, t):
        toks = self._tok(t); tf = {}
        for tk in toks: tf[tk] = tf.get(tk, 0) + 1 / max(len(toks), 1)
        return {tk: v * self._idf.get(tk, 0) for tk, v in tf.items()}

    def _cos(self, v1, v2):
        w = set(v1) | set(v2)
        d = sum(v1.get(p, 0) * v2.get(p, 0) for p in w)
        m1 = math.sqrt(sum(x**2 for x in v1.values()))
        m2 = math.sqrt(sum(x**2 for x in v2.values()))
        return d / (m1 * m2) if m1 and m2 else 0.0

    def _si(self, vm, frases):
        return max((self._cos(vm, self._tfidf(f)) for f in frases), default=0.0)

    def detectar(self, msg: str) -> dict:
        ml = msg.lower().strip(); vm = self._tfidf(ml)
        melhor, score = None, 0.0
        for nome, intent in self.intents.items():
            if intent["exige_ctx"] and self.contexto != intent["exige_ctx"]: continue
            s = self._si(vm, intent["frases"])
            if s > score: score, melhor = s, nome
        if not (melhor and score >= 0.12):
            if self.contexto:
                cands = [(n, i) for n, i in self.intents.items()
                         if i["exige_ctx"] == self.contexto]
                if cands:
                    melhor = max(cands, key=lambda x: self._si(vm, x[1]["frases"]))[0]
                    score = 0.01
                else: melhor = None
            else: melhor = None
        if melhor:
            intent = self.intents[melhor]
            if intent["gera_ctx"] is not None: self.contexto = intent["gera_ctx"]
            ents = self._ext(ml, intent["entidades"]); self.dados.update(ents)
            resp = random.choice(intent["respostas"])
            for k, v in {**self.dados, **ents}.items(): resp = resp.replace(f"{{{k}}}", str(v))
            if intent["acao"]:
                r2 = intent["acao"](ml, self.dados, {})
                if r2: resp = r2
        else:
            melhor, score, ents = "fallback", 0.0, {}
            resp = random.choice(["Nao entendi. Pode reformular?", "Tenta de outro jeito?"])
        return {"intent": melhor, "score": round(score, 2), "resposta": resp,
                "entidades": ents if melhor != "fallback" else {}, "contexto": self.contexto}

    def _ext(self, msg, defs):
        r = {}
        for d in defs:
            for v in d.get("valores", []):
                if v.lower() in msg: r[d["nome"]] = v; break
            if d.get("regex") and d["nome"] not in r:
                m = re.search(d["regex"], msg, re.IGNORECASE)
                if m: r[d["nome"]] = m.group()
        return r

    def resetar(self): self.contexto = None; self.dados = {}

    def chat(self, debug: bool = True):
        """Chat interativo. 'sair' = encerrar | 'reset' = nova conversa"""
        print(f"\n{Fore.CYAN}{'='*54}")
        print(f"  Chatbot Pro: {self.nome}")
        print(f"  'sair' = encerrar | 'reset' = nova conversa")
        print(f"{'='*54}{Style.RESET_ALL}\n")
        while True:
            try:
                user_input = input(f"{Fore.GREEN}Voce >>> {Style.RESET_ALL}").strip()
            except (EOFError, KeyboardInterrupt):
                print(f"\n{Fore.CYAN}  Ate mais!{Style.RESET_ALL}"); break
            if not user_input: continue
            if user_input.lower() == "sair":
                print(f"\n{Fore.CYAN}  Ate mais! 👋{Style.RESET_ALL}"); break
            if user_input.lower() == "reset":
                self.resetar(); print(f"{Fore.YELLOW}  [Nova conversa]{Style.RESET_ALL}\n"); continue
            r = self.detectar(user_input)
            print(f"{Fore.BLUE}Bot  >>> {r['resposta']}{Style.RESET_ALL}")
            if debug:
                print(f"{Fore.WHITE}         [intent: {r['intent']} | "
                      f"certeza: {r['score']:.0%} | "
                      f"contexto: {r['contexto'] or 'nenhum'}]{Style.RESET_ALL}")
            print()

    def simular(self, mensagens):
        for msg in mensagens:
            r = self.detectar(msg)
            print(f"  Voce: {Fore.GREEN}{msg}{Style.RESET_ALL}")
            print(f"  Bot : {Fore.BLUE}{r['resposta']}{Style.RESET_ALL}\n")


# ════════════════════════════════════════════════════════════
# CONFIGURACAO DO BOT (escopo global — acessivel de qualquer celula!)
# ════════════════════════════════════════════════════════════

ESPECIALIDADES = [
    "clinico geral", "cardiologista", "dermatologista",
    "pediatra", "ortopedista", "ginecologista", "oftalmologista",
]
HORARIOS = ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"]

agendamentos = {}
dados_ag     = {}


def ini(msg, dados, ctx):
    dados_ag.clear()
    return (f"Agendamento medico! 🏥\n"
            f"Especialidades:\n"
            f"  {', '.join(ESPECIALIDADES[:4])}\n"
            f"  {', '.join(ESPECIALIDADES[4:])}\n"
            f"Qual voce quer?")


def esp(msg, dados, ctx):
    for e in ESPECIALIDADES:
        if any(p in msg.lower() for p in [e, e.split()[0]]):
            dados_ag["esp"] = e.title()
            return f"{e.title()} selecionado! ✓\nQual e o seu nome completo?"
    return f"Nao encontrei essa especialidade.\nTemos: {', '.join(ESPECIALIDADES[:4])}..."


def salvar_nome(msg, dados, ctx):
    """Extrai apenas o nome proprio — ignora prefixos."""
    nome_extraido = msg
    for prefixo in ["meu nome e ", "me chamo ", "sou o ", "sou a ", "nome "]:
        if prefixo in msg.lower():
            nome_extraido = msg.lower().split(prefixo, 1)[1]
            break
    nome_limpo = nome_extraido.strip().title()
    dados_ag["nome"] = nome_limpo
    return (f"Prazer, {nome_limpo}! 😊\n"
            f"Qual data prefere?\n"
            f"Pode dizer: 'amanha', 'segunda', 'quarta' ou '15/07'")


def salvar_data(msg, dados, ctx):
    hoje = datetime.now()
    DIAS = {"segunda": 0, "terca": 1, "quarta": 2, "quinta": 3, "sexta": 4}
    if "amanha" in msg:
        data = (hoje + timedelta(days=1)).strftime("%d/%m/%Y")
    else:
        data_encontrada = False
        for dia_nome, dia_num in DIAS.items():
            if dia_nome in msg:
                diff = (dia_num - hoje.weekday()) % 7 or 7
                data = (hoje + timedelta(days=diff)).strftime("%d/%m/%Y")
                data_encontrada = True
                break
        if not data_encontrada:
            m = re.search(r"(\d{1,2})/(\d{1,2})", msg)
            if m:
                data = f"{int(m.group(1)):02d}/{int(m.group(2)):02d}/{hoje.year}"
            else:
                data = (hoje + timedelta(days=1)).strftime("%d/%m/%Y")
    dados_ag["data"] = data
    disponiveis = random.sample(HORARIOS, 4)
    dados_ag["horarios_disp"] = disponiveis
    return (f"Data: {data} ✓\n"
            f"Horarios disponíveis:\n"
            f"  {' | '.join(disponiveis)}\n"
            f"Qual prefere?")


def salvar_horario(msg, dados, ctx):
    """Aceita qualquer horario no formato HH:MM — nao depende da lista sorteada."""
    # Tenta encontrar horario no texto: "09:00", "9h", "9 horas", "as 9"
    m = re.search(r"(\d{1,2})[:h](\d{0,2})", msg)
    if m:
        hh = m.group(1).zfill(2)
        mm = m.group(2).zfill(2) if m.group(2) else "00"
        h_str = f"{hh}:{mm}"
        dados_ag["horario"] = h_str
        return (f"Horario {h_str} confirmado! ✓\n\n"
                f"Resumo do agendamento:\n"
                f"  Especialidade: {dados_ag.get('esp', '?')}\n"
                f"  Paciente     : {dados_ag.get('nome', '?')}\n"
                f"  Data         : {dados_ag.get('data', '?')}\n"
                f"  Horario      : {h_str}\n\n"
                f"Confirmar? Responda SIM ou NAO")
    # Verifica lista disponivel como fallback
    for h in dados_ag.get("horarios_disp", HORARIOS):
        if h.replace(":", "") in msg.replace(":", "") or h in msg:
            dados_ag["horario"] = h
            return (f"Horario {h} confirmado! ✓\n"
                    f"Esp: {dados_ag.get('esp')} | Data: {dados_ag.get('data')}\n"
                    f"Confirmar? SIM ou NAO")
    disponiveis = dados_ag.get("horarios_disp", HORARIOS)
    return f"Me diz o horario! Disponíveis: {' | '.join(disponiveis)}"


def confirmar(msg, dados, ctx):
    if "sim" in msg.lower() or "confirm" in msg.lower() or "pode" in msg.lower():
        cod = f"AG-{random.randint(10000, 99999)}"
        agendamentos[cod] = dados_ag.copy()
        return (f"AGENDAMENTO CONFIRMADO! ✅\n\n"
                f"  Codigo       : {cod}\n"
                f"  Especialidade: {dados_ag.get('esp', '?')}\n"
                f"  Paciente     : {dados_ag.get('nome', '?')}\n"
                f"  Data         : {dados_ag.get('data', '?')}\n"
                f"  Horario      : {dados_ag.get('horario', '?')}\n\n"
                f"Lembrete enviado por e-mail!")
    return "Agendamento cancelado. Diz 'agendar' para recomecar!"


bot = MiniDialogflowPro("AgendaBot")

bot.treinar_intent(
    nome="iniciar",
    frases=["agendar", "marcar consulta", "quero medico",
            "consulta", "quero agendar", "marcar"],
    respostas=["Iniciando agendamento..."],
    gera_ctx="esp", acao=ini
)
bot.treinar_intent(
    nome="esp_escolha",
    frases=ESPECIALIDADES + ["clinico", "cardio", "derma", "pediatra", "ortopedia"],
    respostas=["Registrando especialidade..."],
    exige_ctx="esp", gera_ctx="nome_pac", acao=esp
)
bot.treinar_intent(
    nome="nome_pac",
    frases=["meu nome e", "me chamo", "sou", "nome", "chamo"],
    respostas=["Registrando nome..."],
    exige_ctx="nome_pac", gera_ctx="data_c", acao=salvar_nome
)
bot.treinar_intent(
    nome="data_c",
    frases=["amanha", "segunda", "terca", "quarta", "quinta", "sexta",
            "semana", "proximo", "dia"],
    entidades=[{"nome": "data_txt", "regex": r"\d{1,2}/\d{1,2}"}],
    respostas=["Verificando disponibilidade..."],
    exige_ctx="data_c", gera_ctx="hor_c", acao=salvar_data
)
bot.treinar_intent(
    nome="hor_c",
    frases=HORARIOS + ["manha", "tarde", "hora", "horas", "cedo"],
    respostas=["Verificando horario..."],
    exige_ctx="hor_c", gera_ctx="conf_c", acao=salvar_horario
)
bot.treinar_intent(
    nome="conf_c",
    frases=["sim", "confirmo", "pode", "ok", "confirmado",
            "nao", "cancela", "cancelar"],
    respostas=["Processando..."],
    exige_ctx="conf_c", acao=confirmar
)
bot.treinar_intent(
    nome="cancelar_ag",
    frases=["cancelar agendamento", "desmarcar", "nao quero mais consulta"],
    respostas=["Agendamento cancelado! Diz 'agendar' para remarcar."],
)


# ════════════════════════════════════════════════════════════
# TESTES AUTOMATICOS
# ════════════════════════════════════════════════════════════

print(f"\n{Fore.YELLOW}{'='*50}")
print("  SIMULANDO AGENDAMENTO COMPLETO")
print(f"{'='*50}{Style.RESET_ALL}\n")

bot.simular([
    "quero agendar uma consulta",
    "cardiologista",
    "meu nome e Joao Silva",
    "amanha",
    "09:00",
    "sim",
])

print(f"\n{Fore.GREEN}Agendamentos realizados: {list(agendamentos.keys())}{Style.RESET_ALL}")

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
