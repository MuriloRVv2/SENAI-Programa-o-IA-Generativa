# ==============================================================================
#  STT — AVANÇADO  —  "PERGUNTE À CÂMERA"  (STT + Visão Computacional juntos)
# ==============================================================================
#
#  OBJETIVO: o grande encontro da aula! Você FALA uma pergunta e o computador
#  OLHA pela câmera (ou numa foto) e RESPONDE em texto. Ex:
#     - "o que você está vendo?"   -> lista os objetos detectados
#     - "quantas pessoas?"         -> conta as pessoas
#     - "tem celular?"             -> responde sim/não
#
#  ANALOGIA: é juntar o OUVIDO (STT) com o OLHO (YOLO) e um pedacinho de
#  CÉREBRO (umas regrinhas que interpretam a pergunta). Vira um mini-assistente
#  que enxerga. É assim, no fundo, que assistentes "multimodais" funcionam:
#  vários sentidos trabalhando juntos.
#
#  COMO RODAR:
#    - Colab: você envia 1 áudio (.wav com a pergunta) + 1 foto. Ele responde.
#    - PC: você fala no microfone e ele olha pela WEBCAM. Responde na hora.
#  Instale:  pip install ultralytics SpeechRecognition  (e pyaudio no PC)
# ==============================================================================

import cv2
from util_ambiente import escolher_arquivo, webcam_disponivel, estou_no_colab

try:
    import speech_recognition as sr
    from ultralytics import YOLO
except ImportError:
    print("Instale:  pip install ultralytics SpeechRecognition")
    raise SystemExit


MODELO = "yolov8n.pt"

# Tradução PT dos nomes mais comuns do COCO (pra resposta ficar amigável).
TRADUCAO = {
    "person": "pessoa", "cell phone": "celular", "laptop": "notebook",
    "bottle": "garrafa", "cup": "copo", "chair": "cadeira", "book": "livro",
    "dog": "cachorro", "cat": "gato", "car": "carro", "tv": "tv",
    "keyboard": "teclado", "mouse": "mouse", "backpack": "mochila",
}


def detectar_objetos(modelo, imagem):
    """Devolve uma lista com os nomes (em PT) dos objetos detectados."""
    resultados = modelo(imagem, verbose=False)
    nomes = []
    for caixa in resultados[0].boxes:
        nome_en = modelo.names[int(caixa.cls)]
        nomes.append(TRADUCAO.get(nome_en, nome_en))
    return nomes


def responder(pergunta, objetos):
    """O 'cérebro': interpreta a pergunta e monta a resposta a partir do que viu."""
    p = pergunta.lower()

    if "quant" in p:  # "quantas pessoas", "quantos copos"...
        # tenta achar de qual objeto ele fala
        for obj in set(objetos):
            if obj in p:
                qtd = objetos.count(obj)
                return f"Vejo {qtd} {obj}(s)."
        return f"Vejo {len(objetos)} objeto(s) no total."

    if "tem " in p or "há " in p:  # "tem celular?"
        for obj in set(TRADUCAO.values()):
            if obj in p:
                return "Sim, tem!" if obj in objetos else "Não, não vejo isso."
        return "Não entendi qual objeto procurar."

    # "o que você está vendo?" / padrão
    if not objetos:
        return "Não estou vendo nada que eu reconheça."
    contagem = {o: objetos.count(o) for o in set(objetos)}
    partes = [f"{q} {o}(s)" for o, q in contagem.items()]
    return "Estou vendo: " + ", ".join(partes) + "."


def obter_pergunta(rec):
    """Pega a pergunta por microfone (PC) ou por arquivo de áudio (Colab)."""
    if estou_no_colab() or not webcam_disponivel():
        print("\nEnvie um ÁUDIO .wav com sua pergunta:")
        caminho = escolher_arquivo()
        if not caminho:
            return ""
        with sr.AudioFile(caminho) as fonte:
            audio = rec.record(fonte)
    else:
        with sr.Microphone() as fonte:
            print("\n🎤 Faça sua pergunta (ex: 'o que você está vendo?')")
            rec.adjust_for_ambient_noise(fonte, duration=0.5)
            audio = rec.listen(fonte, phrase_time_limit=5)
    try:
        return rec.recognize_google(audio, language="pt-BR")
    except Exception:
        print("Não entendi a pergunta.")
        return ""


def obter_imagem():
    """Pega a imagem por webcam (PC) ou por arquivo (Colab)."""
    if estou_no_colab() or not webcam_disponivel():
        print("\nEnvie uma FOTO pra eu analisar:")
        caminho = escolher_arquivo()
        return cv2.imread(caminho) if caminho else None
    else:
        cam = cv2.VideoCapture(0)
        ok, quadro = cam.read()
        cam.release()
        return quadro if ok else None


def main():
    print("=" * 60)
    print(" STT AVANÇADO — Pergunte à câmera (STT + YOLO)")
    print("=" * 60)

    print("\nCarregando o YOLO...")
    modelo = YOLO(MODELO)
    rec = sr.Recognizer()

    pergunta = obter_pergunta(rec)
    if not pergunta:
        return
    print(f"   Pergunta entendida: '{pergunta}'")

    imagem = obter_imagem()
    if imagem is None:
        print("Não consegui obter a imagem.")
        return

    objetos = detectar_objetos(modelo, imagem)
    resposta = responder(pergunta, objetos)

    print("\n🤖 Resposta:", resposta)

    # (Opcional) Falar a resposta em voz alta — TTS. Descomente se instalar pyttsx3:
    # import pyttsx3; voz = pyttsx3.init(); voz.say(resposta); voz.runAndWait()


if __name__ == "__main__":
    main()
