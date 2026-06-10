# ==============================================================================
#  EXEMPLO FÁCIL 2  — "ACHANDO ROSTOS"  (Detecção de rosto com Haar Cascade)
# ==============================================================================
#  VERSÃO ADAPTADA PARA A INTERFACE GRÁFICA (PyQt6)
#  Separação entre lógica de detecção e exibição.
# ==============================================================================

import sys
import cv2

# O OpenCV já vem com vários "detetives" prontos. Este é o de rosto frontal.
CAMINHO_DETECTOR = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"


def estou_no_colab():
    try:
        import google.colab  # noqa: F401
        return True
    except ImportError:
        return False


def webcam_disponivel():
    return not estou_no_colab()


def carregar_detector():
    """Carrega e retorna o classificador Haar."""
    return cv2.CascadeClassifier(CAMINHO_DETECTOR)


def detectar_rostos(imagem, detector=None, escala=1.1, vizinhos=5):
    """
    Detecta rostos e desenha retângulos verdes.
    Retorna (imagem_anotada, quantidade_de_rostos).
    """
    if detector is None:
        detector = carregar_detector()

    resultado = imagem.copy()
    cinza = cv2.cvtColor(resultado, cv2.COLOR_BGR2GRAY)
    rostos = detector.detectMultiScale(cinza, scaleFactor=escala, minNeighbors=vizinhos)
    n = len(rostos)

    for (x, y, largura, altura) in rostos:
        # Retângulo verde
        cv2.rectangle(resultado, (x, y), (x + largura, y + altura), (0, 220, 100), 3)
        # Mini label
        cv2.putText(resultado, "rosto", (x, y - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 220, 100), 2)

    return resultado, n


def processar_imagem_rostos(caminho: str, detector=None):
    """
    Carrega imagem, detecta rostos e retorna dicionário com resultados.
    """
    imagem = cv2.imread(caminho)
    if imagem is None:
        return None

    if detector is None:
        detector = carregar_detector()

    anotada, n_rostos = detectar_rostos(imagem, detector)
    return {
        "original": imagem,
        "anotada":  anotada,
        "n_rostos": n_rostos,
    }


def abrir_camera():
    """Abre a webcam testando índices e backends (robusto para Windows)."""
    backends = [cv2.CAP_DSHOW, cv2.CAP_ANY] if sys.platform.startswith("win") else [cv2.CAP_ANY]
    for indice in (0, 1, 2):
        for backend in backends:
            camera = cv2.VideoCapture(indice, backend)
            if camera.isOpened():
                ok, _ = camera.read()
                if ok:
                    return camera
            camera.release()
    return None


# ── execução standalone (sem a GUI) ──────────────────────────────────────────
if __name__ == "__main__":
    from util_ambiente import mostrar_imagem, escolher_arquivo

    print("=" * 60)
    print(" EXEMPLO FÁCIL 2 — Detectando rostos com Haar Cascade")
    print("=" * 60)

    detector = carregar_detector()

    if webcam_disponivel():
        print("\nEscolha:")
        print("  1 - Usar uma FOTO")
        print("  2 - Usar a WEBCAM ao vivo")
        escolha = input("Digite 1 ou 2: ").strip()
    else:
        escolha = "1"

    if escolha == "2":
        print("\nWebcam ligada — pressione 'q' pra sair.")
        camera = abrir_camera()
        if camera is None:
            print("❌ Não consegui abrir a webcam.")
        else:
            while True:
                ok, quadro = camera.read()
                if not ok:
                    break
                anotado, n = detectar_rostos(quadro, detector)
                cv2.imshow(f"Webcam — {n} rosto(s) — 'q' pra sair", anotado)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            camera.release()
            cv2.destroyAllWindows()
    else:
        caminho = escolher_arquivo()
        if caminho:
            resultado = processar_imagem_rostos(caminho, detector)
            if resultado:
                print(f">> Encontrei {resultado['n_rostos']} rosto(s)!")
                mostrar_imagem(resultado["anotada"], "Rostos detectados")
                cv2.imwrite("rostos_detectados.jpg", resultado["anotada"])
                print("Salvei como 'rostos_detectados.jpg'.")
