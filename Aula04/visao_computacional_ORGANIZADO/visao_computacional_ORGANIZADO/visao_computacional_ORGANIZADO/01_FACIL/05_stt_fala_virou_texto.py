# ==============================================================================
#  STT — FÁCIL  — "FALA VIROU TEXTO"
# ==============================================================================
#  VERSÃO ADAPTADA PARA A INTERFACE GRÁFICA (PyQt6)
# ==============================================================================

import threading


def estou_no_colab():
    try:
        import google.colab  # noqa: F401
        return True
    except ImportError:
        return False


def transcrever_microfone(callback_status=None, callback_resultado=None):
    """
    Grava do microfone e transcreve. Pode receber callbacks para atualizar a GUI.
    callback_status(str)    — chamado com mensagens de progresso
    callback_resultado(str) — chamado com o texto transcrito (ou mensagem de erro)
    """
    try:
        import speech_recognition as sr
    except ImportError:
        msg = "Instale com: pip install SpeechRecognition pyaudio"
        if callback_resultado:
            callback_resultado(msg)
        return

    def _gravar():
        rec = sr.Recognizer()
        try:
            with sr.Microphone() as fonte:
                if callback_status:
                    callback_status("🎤 Ajustando ao ruído ambiente...")
                rec.adjust_for_ambient_noise(fonte, duration=0.5)
                if callback_status:
                    callback_status("🎤 Fale agora! (até 8 segundos)")
                audio = rec.listen(fonte, phrase_time_limit=8)
            if callback_status:
                callback_status("⏳ Processando...")
            texto = rec.recognize_google(audio, language="pt-BR")
            if callback_resultado:
                callback_resultado(texto)
        except Exception as e:
            msg = f"Erro: {e}"
            if callback_resultado:
                callback_resultado(msg)

    t = threading.Thread(target=_gravar, daemon=True)
    t.start()
    return t


def transcrever_arquivo_audio(caminho: str, callback_resultado=None):
    """Transcreve um arquivo .wav."""
    try:
        import speech_recognition as sr
    except ImportError:
        msg = "Instale com: pip install SpeechRecognition"
        if callback_resultado:
            callback_resultado(msg)
        return

    def _transcrever():
        rec = sr.Recognizer()
        try:
            with sr.AudioFile(caminho) as fonte:
                audio = rec.record(fonte)
            texto = rec.recognize_google(audio, language="pt-BR")
            if callback_resultado:
                callback_resultado(texto)
        except Exception as e:
            if callback_resultado:
                callback_resultado(f"Erro: {e}")

    t = threading.Thread(target=_transcrever, daemon=True)
    t.start()
    return t


# ── execução standalone ───────────────────────────────────────────────────────
if __name__ == "__main__":
    from util_ambiente import escolher_arquivo

    print("=" * 60)
    print(" STT FÁCIL — Fala virou texto")
    print("=" * 60)

    if estou_no_colab():
        escolha = "2"
    else:
        print("\n  1 - MICROFONE")
        print("  2 - ARQUIVO de áudio (.wav)")
        escolha = input("Digite 1 ou 2: ").strip()

    resultado_final = {}

    def on_resultado(texto):
        print(f"\n📝 Resultado: {texto}")
        resultado_final["texto"] = texto

    if escolha == "2":
        caminho = escolher_arquivo(tipos="Áudio (*.wav);;Todos os arquivos (*.*)")
        if caminho:
            t = transcrever_arquivo_audio(caminho, callback_resultado=on_resultado)
            t.join()
    else:
        t = transcrever_microfone(
            callback_status=lambda s: print(s),
            callback_resultado=on_resultado,
        )
        t.join()
