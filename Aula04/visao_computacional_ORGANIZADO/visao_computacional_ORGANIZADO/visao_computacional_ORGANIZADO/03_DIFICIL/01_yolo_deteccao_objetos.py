# ==============================================================================
#  EXEMPLO DIFÍCIL 1  —  "O OLHO BIÔNICO"  (Detecção de objetos com YOLO)
# ==============================================================================
#
#  OBJETIVO: detectar VÁRIOS objetos ao mesmo tempo (pessoa, carro, cachorro,
#  celular, garrafa...) numa imagem, vídeo ou webcam — tudo de uma vez.
#
#  O QUE É YOLO? Significa "You Only Look Once" (Você Olha Só Uma Vez).
#  ANALOGIA: o Haar Cascade da Etapa 1 era um detetive que só procurava UMA
#  coisa (rosto) e passava a lupa devagar pela imagem. O YOLO é um craque que
#  bate o olho na imagem INTEIRA UMA vez só e já fala: "tem 2 pessoas ali, 1
#  carro acolá e um cachorro no canto". Rápido e esperto.
#
#  Ele já vem "treinado de fábrica" para reconhecer 80 tipos de objetos do
#  dia a dia (o conjunto COCO). No próximo exemplo a gente TREINA o nosso!
#
#  COMO RODAR:
#    - Colab:  !pip install ultralytics   (depois rode normalmente, modo foto)
#    - PC:     pip install ultralytics    (foto, vídeo OU webcam ao vivo)
#  Na primeira vez, ele baixa o "cérebro" do modelo (yolov8n.pt) sozinho.
# ==============================================================================

import cv2
from util_ambiente import mostrar_imagem, escolher_arquivo, webcam_disponivel

try:
    from ultralytics import YOLO
except ImportError:
    print("Instale o YOLO com:  pip install ultralytics")
    raise SystemExit


# "n" = nano = o menor e mais rápido (ótimo pra aula). Existem s, m, l, x (maiores/melhores).
MODELO = "yolov8n.pt"


def detectar_imagem(modelo):
    print("\nEscolha uma foto com vários objetos (rua, sala, etc.):")
    caminho = escolher_arquivo()
    if not caminho:
        return

    # Uma linha só faz a mágica acontecer:
    resultados = modelo(caminho)

    # resultados[0].plot() devolve a imagem JÁ com as caixas e nomes desenhados.
    anotada = resultados[0].plot()

    # Lista o que ele achou (no terminal).
    print("\n>> Objetos encontrados:")
    for caixa in resultados[0].boxes:
        classe = modelo.names[int(caixa.cls)]
        confianca = float(caixa.conf) * 100
        print(f"   - {classe} ({confianca:.0f}% de certeza)")

    mostrar_imagem(anotada, "Deteccao YOLO")
    cv2.imwrite("yolo_resultado.jpg", anotada)
    print("Salvei como 'yolo_resultado.jpg'.")


def detectar_video(modelo):
    print("\nEscolha um arquivo de vídeo (.mp4):")
    caminho = escolher_arquivo()
    if not caminho:
        return
    cap = cv2.VideoCapture(caminho)
    while True:
        ok, quadro = cap.read()
        if not ok:
            break
        resultados = modelo(quadro, verbose=False)
        anotada = resultados[0].plot()
        cv2.imshow("YOLO no video - 'q' pra sair", anotada)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()


def detectar_webcam(modelo):
    print("\nWebcam ligada — apontando o 'olho biônico'. Aperte 'q' pra sair.")
    cam = cv2.VideoCapture(0)
    while True:
        ok, quadro = cam.read()
        if not ok:
            break
        resultados = modelo(quadro, verbose=False)
        anotada = resultados[0].plot()
        cv2.imshow("YOLO ao vivo - 'q' pra sair", anotada)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cam.release()
    cv2.destroyAllWindows()


def main():
    print("=" * 60)
    print(" EXEMPLO DIFÍCIL 1 — Detecção de objetos com YOLO")
    print("=" * 60)

    print("\nCarregando o cérebro do YOLO (pode baixar na 1ª vez)...")
    modelo = YOLO(MODELO)

    if webcam_disponivel():
        print("\nEscolha o modo:")
        print("  1 - FOTO (arquivo externo)")
        print("  2 - VÍDEO (arquivo externo)")
        print("  3 - WEBCAM ao vivo")
        escolha = input("Digite 1, 2 ou 3: ").strip()
        if escolha == "2":
            detectar_video(modelo)
        elif escolha == "3":
            detectar_webcam(modelo)
        else:
            detectar_imagem(modelo)
    else:
        print("\nVocê está no Colab — vamos detectar numa FOTO.")
        detectar_imagem(modelo)


if __name__ == "__main__":
    main()
