# ==============================================================================
#  OPENCV — AVANÇADO  —  "SCANNER DE DOCUMENTOS"  (correção de perspectiva)
# ==============================================================================
#
#  OBJETIVO: pegar a foto torta de uma folha/documento (tirada de qualquer
#  ângulo) e "achatar" como se fosse um scanner de verdade. É o que apps tipo
#  CamScanner fazem.
#
#  COMO FUNCIONA (a sacada genial):
#    1) Achamos as BORDAS da imagem (Canny).
#    2) Procuramos o maior contorno que tenha 4 CANTOS (a folha é um retângulo).
#    3) Fazemos uma TRANSFORMAÇÃO DE PERSPECTIVA: "puxamos" os 4 cantos da folha
#       torta para os 4 cantos de um retângulo reto.
#  ANALOGIA: é como pegar um pôster colado torto na parede e, num passe de
#  mágica, esticá-lo para ficar perfeitamente reto e de frente pra você.
#
#  COMO RODAR: Colab (foto de um documento) ou PC.
# ==============================================================================

import cv2
import numpy as np
from util_ambiente import mostrar_imagem, escolher_arquivo


def ordenar_cantos(pontos):
    """Coloca os 4 cantos sempre na ordem: topo-esq, topo-dir, baixo-dir, baixo-esq."""
    pontos = pontos.reshape(4, 2)
    ordenado = np.zeros((4, 2), dtype="float32")
    soma = pontos.sum(axis=1)
    ordenado[0] = pontos[np.argmin(soma)]   # topo-esquerda  (menor x+y)
    ordenado[2] = pontos[np.argmax(soma)]   # baixo-direita  (maior x+y)
    dif = np.diff(pontos, axis=1)
    ordenado[1] = pontos[np.argmin(dif)]    # topo-direita
    ordenado[3] = pontos[np.argmax(dif)]    # baixo-esquerda
    return ordenado


def escanear(img):
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cinza = cv2.GaussianBlur(cinza, (5, 5), 0)
    bordas = cv2.Canny(cinza, 75, 200)

    contornos, _ = cv2.findContours(bordas, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contornos = sorted(contornos, key=cv2.contourArea, reverse=True)[:5]

    folha = None
    for c in contornos:
        perimetro = cv2.arcLength(c, True)
        # approxPolyDP "simplifica" o contorno; se sobrar 4 pontos, achamos a folha.
        aprox = cv2.approxPolyDP(c, 0.02 * perimetro, True)
        if len(aprox) == 4:
            folha = aprox
            break

    if folha is None:
        print("Não encontrei um documento de 4 cantos. Tente uma foto mais nítida e contrastada.")
        return None

    cantos = ordenar_cantos(folha)
    (tl, tr, br, bl) = cantos

    # Calcula o tamanho do documento "achatado".
    largura = int(max(np.linalg.norm(br - bl), np.linalg.norm(tr - tl)))
    altura = int(max(np.linalg.norm(tr - br), np.linalg.norm(tl - bl)))

    destino = np.array([[0, 0], [largura - 1, 0],
                        [largura - 1, altura - 1], [0, altura - 1]], dtype="float32")

    # A matriz que "puxa" os 4 cantos tortos para os 4 cantos retos.
    matriz = cv2.getPerspectiveTransform(cantos, destino)
    achatado = cv2.warpPerspective(img, matriz, (largura, altura))
    return achatado


def main():
    print("=" * 60)
    print(" OPENCV AVANÇADO — Scanner de documentos")
    print("=" * 60)
    print("\nEscolha a foto de um documento/folha (de preferência sobre fundo escuro):")
    caminho = escolher_arquivo()
    if not caminho:
        return
    img = cv2.imread(caminho)
    if img is None:
        print("Não consegui abrir a imagem.")
        return

    resultado = escanear(img)
    if resultado is None:
        return

    mostrar_imagem(resultado, "Documento escaneado")
    # Versão preto e branco estilo "scanner".
    pb = cv2.adaptiveThreshold(cv2.cvtColor(resultado, cv2.COLOR_BGR2GRAY), 255,
                               cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 10)
    mostrar_imagem(pb, "Versao 'scanner' P&B")
    cv2.imwrite("documento_escaneado.jpg", pb)
    print("Salvei como 'documento_escaneado.jpg'.")


if __name__ == "__main__":
    main()
