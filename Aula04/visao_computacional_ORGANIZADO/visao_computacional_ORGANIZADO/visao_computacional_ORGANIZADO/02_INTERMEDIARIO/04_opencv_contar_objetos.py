# ==============================================================================
#  OPENCV — INTERMEDIÁRIO  —  "CONTANDO OBJETOS"  (limiar + contornos)
# ==============================================================================
#
#  OBJETIVO: contar automaticamente quantos objetos há numa foto (ex: moedas,
#  feijões, tampinhas sobre uma mesa) SEM usar IA pesada — só OpenCV puro.
#
#  COMO FUNCIONA (3 passos, com analogia):
#    1) Preto e branco -> mais fácil de processar.
#    2) LIMIAR (threshold): vira tudo "ou branco ou preto". É como um interruptor:
#       pixel claro o bastante? vira BRANCO (objeto). Senão, PRETO (fundo).
#    3) CONTORNOS: o OpenCV "passa o dedo" no contorno de cada mancha branca e
#       devolve uma lista. Quantas manchas = quantos objetos. Contamos a lista.
#
#  DICA: funciona melhor com objetos destacados num fundo liso e claro/escuro.
#  COMO RODAR: Colab (foto enviada) ou PC.
# ==============================================================================

import cv2
from util_ambiente import mostrar_imagem, escolher_arquivo


def contar_objetos(img, area_minima=500):
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Desfoque leve pra reduzir "sujeira" antes de separar objeto do fundo.
    cinza = cv2.GaussianBlur(cinza, (7, 7), 0)

    # Limiar automático (Otsu escolhe sozinho o melhor "ponto de corte").
    # THRESH_BINARY_INV: objetos escuros viram branco. Troque pra BINARY se o
    # seu objeto for mais CLARO que o fundo.
    _, limiar = cv2.threshold(cinza, 0, 255,
                              cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    contornos, _ = cv2.findContours(limiar, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Ignora manchas minúsculas (ruído) e desenha + numera o que sobrou.
    contador = 0
    for c in contornos:
        if cv2.contourArea(c) < area_minima:
            continue
        contador += 1
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(img, str(contador), (x, y - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    cv2.putText(img, f"Total: {contador}", (15, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    return img, contador


def main():
    print("=" * 60)
    print(" OPENCV INTERMEDIÁRIO — Contando objetos")
    print("=" * 60)
    print("\nEscolha uma foto com vários objetos num fundo liso (moedas, grãos...):")
    caminho = escolher_arquivo()
    if not caminho:
        return
    img = cv2.imread(caminho)
    if img is None:
        print("Não consegui abrir a imagem.")
        return

    resultado, total = contar_objetos(img)
    print(f"\n>> Contei {total} objeto(s)!")
    mostrar_imagem(resultado, "Contagem de objetos")
    cv2.imwrite("opencv_contagem.jpg", resultado)
    print("Salvei como 'opencv_contagem.jpg'.")
    print("Dica: se contou errado, ajuste 'area_minima' ou troque BINARY_INV por BINARY.")


if __name__ == "__main__":
    main()
