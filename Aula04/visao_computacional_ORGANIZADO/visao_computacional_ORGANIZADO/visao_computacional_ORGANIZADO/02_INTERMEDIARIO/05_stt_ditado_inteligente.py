# ==============================================================================
#  STT — INTERMEDIÁRIO  —  "DITADO INTELIGENTE"  (ditar e salvar em arquivo)
# ==============================================================================
#
#  OBJETIVO: transformar o STT num "bloco de notas por voz". Você dita e o texto
#  vai sendo salvo num arquivo. Alguns COMANDOS de voz controlam a escrita:
#     - "nova linha"  -> pula uma linha
#     - "apagar"      -> apaga a última frase
#     - "parar"       -> encerra e salva
#
#  ANALOGIA: é como ter um estagiário que digita o que você fala E entende
#  ordens simples ("pula linha aí!", "apaga isso!"). A diferença pro Fácil é
#  que agora o programa NÃO só transcreve — ele DECIDE o que fazer com o texto.
#
#  COMO RODAR:
#    - PC: microfone (loop contínuo de ditado).
#    - Colab: modo demonstração com uma lista de frases simuladas (sem mic).
# ==============================================================================

from util_ambiente import webcam_disponivel, estou_no_colab

try:
    import speech_recognition as sr
except ImportError:
    print("Instale com:  pip install SpeechRecognition pyaudio")
    raise SystemExit

ARQUIVO_SAIDA = "meu_ditado.txt"


def aplicar_comando(linhas, fala):
    """Decide o que fazer com a fala. Retorna (continuar?, mensagem)."""
    f = fala.lower().strip()
    if "parar" in f or "encerrar" in f:
        return False, "Encerrando e salvando."
    if "nova linha" in f:
        linhas.append("")
        return True, "(nova linha)"
    if "apagar" in f:
        if linhas:
            removido = linhas.pop()
            return True, f"(apaguei: '{removido}')"
        return True, "(nada pra apagar)"
    # Caso normal: é texto pra escrever.
    linhas.append(fala)
    return True, f"+ {fala}"


def salvar(linhas):
    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))
    print(f"\n💾 Ditado salvo em '{ARQUIVO_SAIDA}'.")


def modo_microfone():
    rec = sr.Recognizer()
    linhas = []
    print("\n🎤 Pode ditar! (diga 'nova linha', 'apagar' ou 'parar')")
    while True:
        with sr.Microphone() as fonte:
            rec.adjust_for_ambient_noise(fonte, duration=0.4)
            audio = rec.listen(fonte, phrase_time_limit=6)
        try:
            fala = rec.recognize_google(audio, language="pt-BR")
        except sr.UnknownValueError:
            print("   (não entendi, repita)")
            continue
        except sr.RequestError:
            print("   (sem internet)")
            break

        continuar, msg = aplicar_comando(linhas, fala)
        print("  ", msg)
        if not continuar:
            break
    salvar(linhas)


def modo_demo():
    """No Colab, simula um ditado pra mostrar a lógica dos comandos."""
    print("\nModo DEMONSTRAÇÃO (Colab, sem microfone):")
    falas_simuladas = [
        "olá pessoal", "nova linha", "hoje estudamos visão computacional",
        "essa frase está errada", "apagar", "parar",
    ]
    linhas = []
    for fala in falas_simuladas:
        continuar, msg = aplicar_comando(linhas, fala)
        print(f"  ouvi '{fala}'  ->  {msg}")
        if not continuar:
            break
    salvar(linhas)
    print("Conteúdo final:")
    print("-" * 30)
    print("\n".join(linhas))


def main():
    print("=" * 60)
    print(" STT INTERMEDIÁRIO — Ditado inteligente")
    print("=" * 60)
    if estou_no_colab() or not webcam_disponivel():
        modo_demo()
    else:
        modo_microfone()


if __name__ == "__main__":
    main()
