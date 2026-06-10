# ==============================================================================
#  EXEMPLO INTERMEDIÁRIO 2  —  "CAÇA AO OBJETO"  (Detecção por cor + movimento)
# ==============================================================================
#
#  OBJETIVO: detectar e "perseguir" um objeto pela COR (ex: uma bolinha
#  vermelha) e também detectar MOVIMENTO numa cena.
#
#  ANALOGIA 1 (cor): pra nós, "vermelho" é só uma sensação. Pro computador, é
#  uma FAIXA de números. É como um segurança que só deixa passar quem tem
#  pulseira de uma cor específica — ele recorta da imagem só o que é "vermelho"
#  e ignora o resto. Esse recorte se chama "máscara".
#
#  ANALOGIA 2 (movimento): pra achar movimento, comparamos o quadro de AGORA
#  com o de um instante ATRÁS. O que mudou de lugar "acende". É igual àquela
#  brincadeira de "achar as diferenças" entre duas figuras quase iguais.
#
#  DICA: usamos o espaço de cor HSV (Matiz, Saturação, Valor) em vez de RGB
#  porque nele é MUITO mais fácil dizer "essa faixa é vermelha", mesmo com a
#  luz mudando. Pensa no H como uma roda de cores (0=vermelho, 60=verde...).
#
#  COMO RODAR:
#    - PC: webcam ao vivo (mais divertido!) ou vídeo/foto externa.
#    - Colab: use foto ou vídeo enviado (sem webcam ao vivo).
# ==============================================================================

import cv2
import numpy as np
from util_ambiente import mostrar_imagem, escolher_arquivo, webcam_disponivel


# Faixa de cor a perseguir (padrão: VERMELHO). Em HSV o vermelho fica nas pontas.
# Você pode trocar pra azul/verde mudando esses números (explicado no .docx).
VERMELHO_BAIXO_1 = np.array([0, 120, 70])
VERMELHO_ALTO_1 = np.array([10, 255, 255])
VERMELHO_BAIXO_2 = np.array([170, 120, 70])
VERMELHO_ALTO_2 = np.array([180, 255, 255])


def detectar_cor(quadro):
    """Acha as regiões VERMELHAS e desenha um retângulo em volta delas."""
    hsv = cv2.cvtColor(quadro, cv2.COLOR_BGR2HSV)

    # Como o vermelho fica nas duas pontas da roda de cores, somamos 2 máscaras.
    mascara1 = cv2.inRange(hsv, VERMELHO_BAIXO_1, VERMELHO_ALTO_1)
    mascara2 = cv2.inRange(hsv, VERMELHO_BAIXO_2, VERMELHO_ALTO_2)
    mascara = mascara1 + mascara2

    # Acha os "contornos" (os blocos de cor) e marca o maior deles.
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contornos:
        maior = max(contornos, key=cv2.contourArea)
        if cv2.contourArea(maior) > 500:  # ignora pontinhos minúsculos (ruído)
            x, y, w, h = cv2.boundingRect(maior)
            cv2.rectangle(quadro, (x, y), (x + w, y + h), (0, 255, 0), 3)
            cv2.putText(quadro, "Objeto vermelho!", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    return quadro


def modo_cor_imagem():
    print("\nEscolha uma foto com algum objeto VERMELHO:")
    caminho = escolher_arquivo()
    if not caminho:
        return
    img = cv2.imread(caminho)
    if img is None:
        print("Não consegui abrir a imagem.")
        return
    resultado = detectar_cor(img)
    mostrar_imagem(resultado, "Deteccao por cor")
    cv2.imwrite("deteccao_cor.jpg", resultado)
    print("Salvei como 'deteccao_cor.jpg'.")


def modo_cor_webcam():
    print("\nWebcam ligada — mostre um objeto VERMELHO. Aperte 'q' pra sair.")
    cam = cv2.VideoCapture(0)
    while True:
        ok, quadro = cam.read()
        if not ok:
            break
        quadro = detectar_cor(quadro)
        cv2.imshow("Caca ao objeto vermelho - 'q' pra sair", quadro)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cam.release()
    cv2.destroyAllWindows()


def modo_movimento_webcam():
    """Detecta movimento comparando cada quadro com o anterior."""
    print("\nWebcam ligada — detectando MOVIMENTO. Fique parado e depois mexa! 'q' pra sair.")
    cam = cv2.VideoCapture(0)
    ok, anterior = cam.read()
    anterior_cinza = cv2.cvtColor(anterior, cv2.COLOR_BGR2GRAY)
    anterior_cinza = cv2.GaussianBlur(anterior_cinza, (21, 21), 0)

    while True:
        ok, quadro = cam.read()
        if not ok:
            break
        cinza = cv2.cvtColor(quadro, cv2.COLOR_BGR2GRAY)
        cinza = cv2.GaussianBlur(cinza, (21, 21), 0)

        # "Achar as diferenças" entre o quadro de agora e o anterior.
        diferenca = cv2.absdiff(anterior_cinza, cinza)
        _, limiar = cv2.threshold(diferenca, 25, 255, cv2.THRESH_BINARY)
        contornos, _ = cv2.findContours(limiar, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in contornos:
            if cv2.contourArea(c) < 800:
                continue
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(quadro, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(quadro, "Movimento!", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        cv2.imshow("Detector de movimento - 'q' pra sair", quadro)
        anterior_cinza = cinza
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cam.release()
    cv2.destroyAllWindows()


def main():
    print("=" * 60)
    print(" EXEMPLO INTERMEDIÁRIO 2 — Detecção por cor + movimento")
    print("=" * 60)

    if webcam_disponivel():
        print("\nEscolha o modo:")
        print("  1 - Detectar COR numa FOTO (arquivo externo)")
        print("  2 - Detectar COR pela WEBCAM ao vivo")
        print("  3 - Detectar MOVIMENTO pela WEBCAM ao vivo")
        escolha = input("Digite 1, 2 ou 3: ").strip()
        if escolha == "2":
            modo_cor_webcam()
        elif escolha == "3":
            modo_movimento_webcam()
        else:
            modo_cor_imagem()
    else:
        print("\nVocê está no Colab — vamos detectar COR numa FOTO.")
        modo_cor_imagem()


if __name__ == "__main__":
    main()
