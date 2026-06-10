# ==============================================================================
#  EXEMPLO INTERMEDIÁRIO 3  —  "CÂMERA, ME OBEDEÇA!"  (STT - Speech to Text)
# ==============================================================================
#
#  OBJETIVO: juntar VOZ + VISÃO. Você FALA um comando e o programa age:
#  fala "foto" -> ele tira uma foto da webcam; fala "sair" -> ele encerra.
#
#  O QUE É STT (Speech to Text)? É transformar SOM em TEXTO. Você fala, o
#  computador escreve o que entendeu. É o que a Alexa/Google faz o tempo todo.
#
#  ANALOGIA: o microfone é um "ouvido". O STT é o "tradutor" que pega o som e
#  escreve em letras. Depois, a gente só compara o texto com uma lista de
#  comandos — tipo um cardápio: "se ouvir 'foto', faça X".
#
#  COMO RODAR:
#    - PC: precisa de microfone + 'pip install SpeechRecognition pyaudio'.
#          (No Windows, se o pyaudio não instalar: pip install pipwin; pipwin install pyaudio)
#    - Colab: o Colab NÃO acessa o microfone direto. Por isso este exemplo
#      tem o MODO ARQUIVO: você envia um áudio (.wav) e ele transcreve.
#
#  Obs: usamos o reconhecedor do Google (precisa de internet).
# ==============================================================================

import cv2
from util_ambiente import escolher_arquivo, webcam_disponivel, estou_no_colab

try:
    import speech_recognition as sr
except ImportError:
    print("Instale com:  pip install SpeechRecognition")
    print("(E pyaudio, pra usar o microfone no PC.)")
    raise SystemExit


def ouvir_do_microfone(reconhecedor):
    """Escuta o microfone e devolve o texto reconhecido (em português)."""
    with sr.Microphone() as fonte:
        print("\n🎤 Pode falar! (ex: 'foto' ou 'sair')")
        reconhecedor.adjust_for_ambient_noise(fonte, duration=0.5)  # ignora barulho de fundo
        audio = reconhecedor.listen(fonte, phrase_time_limit=4)
    try:
        texto = reconhecedor.recognize_google(audio, language="pt-BR")
        print(f"   Você disse: '{texto}'")
        return texto.lower()
    except sr.UnknownValueError:
        print("   Não entendi. Tente de novo.")
        return ""
    except sr.RequestError:
        print("   Sem internet pro reconhecimento. Verifique a conexão.")
        return ""


def ouvir_de_arquivo(reconhecedor):
    """Transcreve um arquivo de áudio .wav (útil no Colab)."""
    print("\nEscolha um arquivo de áudio .wav:")
    caminho = escolher_arquivo()
    if not caminho:
        return ""
    with sr.AudioFile(caminho) as fonte:
        audio = reconhecedor.record(fonte)
    try:
        texto = reconhecedor.recognize_google(audio, language="pt-BR")
        print(f"   Transcrição: '{texto}'")
        return texto.lower()
    except Exception as e:
        print(f"   Não consegui transcrever: {e}")
        return ""


def tirar_foto_webcam():
    """Tira uma foto da webcam e salva."""
    cam = cv2.VideoCapture(0)
    ok, quadro = cam.read()
    cam.release()
    if ok:
        cv2.imwrite("foto_por_voz.jpg", quadro)
        print("   📸 Foto salva como 'foto_por_voz.jpg'!")
    else:
        print("   Não consegui acessar a webcam.")


def main():
    print("=" * 60)
    print(" EXEMPLO INTERMEDIÁRIO 3 — Comando de voz (STT) + câmera")
    print("=" * 60)

    reconhecedor = sr.Recognizer()

    # No Colab (sem microfone), só transcreve um áudio enviado.
    if estou_no_colab() or not webcam_disponivel():
        print("\nModo ARQUIVO (Colab): vou transcrever um áudio que você enviar.")
        texto = ouvir_de_arquivo(reconhecedor)
        if "foto" in texto:
            print("   -> O comando reconhecido foi 'foto' (no PC, isso tiraria uma foto).")
        return

    # No PC: laço de comandos de voz controlando a câmera.
    print("\nComandos disponíveis: diga 'foto' para fotografar, 'sair' para encerrar.")
    while True:
        comando = ouvir_do_microfone(reconhecedor)
        if "foto" in comando:
            tirar_foto_webcam()
        elif "sair" in comando or "encerrar" in comando:
            print("   Até a próxima! 👋")
            break


if __name__ == "__main__":
    main()
