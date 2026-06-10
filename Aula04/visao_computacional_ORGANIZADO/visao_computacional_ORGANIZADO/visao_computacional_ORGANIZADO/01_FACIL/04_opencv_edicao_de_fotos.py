# ==============================================================================
#  OPENCV — FÁCIL  — "MINI APP DE FOTOS"
# ==============================================================================
#  VERSÃO ADAPTADA PARA A INTERFACE GRÁFICA (PyQt6)
# ==============================================================================

import cv2
import numpy as np


def processar_edicao_fotos(caminho: str):
    """
    Aplica edições básicas e retorna dicionário com todos os resultados.
    """
    img = cv2.imread(caminho)
    if img is None:
        return None

    h, w = img.shape[:2]

    # Brilho + contraste
    alfa, beta = 1.3, 40
    ajustada = cv2.convertScaleAbs(img, alpha=alfa, beta=beta)

    # Espelhar
    espelhada = cv2.flip(img, 1)

    # Girar 90°
    girada = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

    # Recorte central (ROI)
    recorte = img[h // 4: 3 * h // 4, w // 4: 3 * w // 4]

    return {
        "original":  img,
        "ajustada":  ajustada,
        "espelhada": espelhada,
        "girada":    girada,
        "recorte":   recorte,
    }


# ── execução standalone ───────────────────────────────────────────────────────
if __name__ == "__main__":
    from util_ambiente import mostrar_imagem, escolher_arquivo

    print("=" * 60)
    print(" OPENCV FÁCIL — Mini app de fotos")
    print("=" * 60)

    caminho = escolher_arquivo()
    if caminho:
        resultado = processar_edicao_fotos(caminho)
        if resultado:
            for nome, img in resultado.items():
                mostrar_imagem(img, nome)
            cv2.imwrite("opencv_editada.jpg", resultado["ajustada"])
            print("Salvei como 'opencv_editada.jpg'.")
