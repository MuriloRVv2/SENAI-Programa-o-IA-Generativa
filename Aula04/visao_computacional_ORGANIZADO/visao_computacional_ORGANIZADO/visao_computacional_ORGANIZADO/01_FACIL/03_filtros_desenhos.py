# ==============================================================================
#  EXEMPLO FÁCIL 3  — "FILTROS E DESENHOS"
# ==============================================================================
#  VERSÃO ADAPTADA PARA A INTERFACE GRÁFICA (PyQt6)
# ==============================================================================

import cv2


def aplicar_todos_os_filtros(imagem):
    """
    Aplica todos os filtros e retorna um dicionário com cada resultado.
    """
    altura, largura = imagem.shape[:2]

    # Borrado
    borrada = cv2.GaussianBlur(imagem, (15, 15), 0)

    # Bordas (Canny) — convertido para 3 canais para exibição uniforme
    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    bordas = cv2.Canny(cinza, 100, 200)
    bordas_3ch = cv2.cvtColor(bordas, cv2.COLOR_GRAY2BGR)

    # Negativo
    negativo = cv2.bitwise_not(imagem)

    # Imagem com desenhos
    desenhada = imagem.copy()
    cv2.rectangle(desenhada, (20, 20), (largura - 20, altura - 20), (0, 200, 100), 4)
    cv2.circle(desenhada, (largura // 2, altura // 2), 40, (60, 60, 220), -1)
    cv2.putText(desenhada, "Visao Computacional!", (30, altura - 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    return {
        "original":  imagem,
        "borrada":   borrada,
        "bordas":    bordas_3ch,
        "negativo":  negativo,
        "desenhada": desenhada,
    }


def processar_imagem_filtros(caminho: str):
    """Carrega imagem e aplica todos os filtros. Retorna dict ou None."""
    imagem = cv2.imread(caminho)
    if imagem is None:
        return None
    return aplicar_todos_os_filtros(imagem)


# ── execução standalone ───────────────────────────────────────────────────────
if __name__ == "__main__":
    from util_ambiente import mostrar_imagem, escolher_arquivo, webcam_disponivel

    print("=" * 60)
    print(" EXEMPLO FÁCIL 3 — Filtros e desenhos (tipo Instagram!)")
    print("=" * 60)

    if webcam_disponivel():
        print("\n  1 - Usar uma FOTO")
        print("  2 - Usar a WEBCAM ao vivo (bordas)")
        escolha = input("Digite 1 ou 2: ").strip()
    else:
        escolha = "1"

    if escolha == "2":
        camera = cv2.VideoCapture(0)
        while True:
            ok, quadro = camera.read()
            if not ok:
                break
            cinza = cv2.cvtColor(quadro, cv2.COLOR_BGR2GRAY)
            bordas = cv2.Canny(cinza, 100, 200)
            cv2.imshow("Bordas ao vivo — 'q' pra sair", bordas)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        camera.release()
        cv2.destroyAllWindows()
    else:
        caminho = escolher_arquivo()
        if caminho:
            resultado = processar_imagem_filtros(caminho)
            if resultado:
                for nome, img in resultado.items():
                    mostrar_imagem(img, nome)
                cv2.imwrite("imagem_com_filtros.jpg", resultado["desenhada"])
                print("Salvei como 'imagem_com_filtros.jpg'.")
