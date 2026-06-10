# ==============================================================================
#  EXEMPLO FÁCIL 1  — "OI, IMAGEM!"  (Os primeiros passos da Visão Computacional)
# ==============================================================================
#  VERSÃO ADAPTADA PARA A INTERFACE GRÁFICA (PyQt6)
#  As funções retornam imagens em vez de chamar mostrar_imagem() diretamente,
#  permitindo exibição dentro da janela da GUI.
# ==============================================================================

import cv2


def carregar_imagem(caminho: str):
    """
    Carrega uma imagem do disco e retorna junto com suas dimensões.
    Retorna (imagem, largura, altura) ou (None, 0, 0) em caso de erro.
    """
    imagem = cv2.imread(caminho)
    if imagem is None:
        return None, 0, 0
    altura, largura = imagem.shape[:2]
    return imagem, largura, altura


def converter_para_cinza(imagem):
    """Converte a imagem para preto e branco (escala de cinza)."""
    return cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)


def redimensionar_metade(imagem):
    """Reduz a imagem para metade do tamanho original."""
    h, w = imagem.shape[:2]
    return cv2.resize(imagem, (w // 2, h // 2))


def processar_imagem(caminho: str):
    """
    Fluxo completo do Exemplo 1.
    Retorna um dicionário com todas as versões processadas da imagem,
    ou None em caso de erro.
    """
    imagem, largura, altura = carregar_imagem(caminho)
    if imagem is None:
        return None

    cinza = converter_para_cinza(imagem)
    # Converte cinza de volta pra 3 canais pra exibir consistentemente na GUI
    cinza_3ch = cv2.cvtColor(cinza, cv2.COLOR_GRAY2BGR)
    menor = redimensionar_metade(imagem)

    return {
        "original":  imagem,
        "cinza":     cinza_3ch,
        "metade":    menor,
        "largura":   largura,
        "altura":    altura,
    }


# ── execução standalone (sem a GUI) ──────────────────────────────────────────
if __name__ == "__main__":
    from util_ambiente import mostrar_imagem, escolher_arquivo

    print("=" * 60)
    print(" EXEMPLO FÁCIL 1 — Mexendo na nossa primeira imagem!")
    print("=" * 60)

    caminho = escolher_arquivo()
    if not caminho:
        print("Nenhum arquivo escolhido.")
    else:
        resultado = processar_imagem(caminho)
        if resultado is None:
            print("Ops! Não consegui abrir essa imagem.")
        else:
            w, h = resultado["largura"], resultado["altura"]
            print(f"\nImagem carregada! Tamanho: {w} x {h} pixels.")
            mostrar_imagem(resultado["original"], "1 - Original (colorida)")
            mostrar_imagem(resultado["cinza"],    "2 - Preto e branco")
            mostrar_imagem(resultado["metade"],   "3 - Metade do tamanho")
            cv2.imwrite("resultado_preto_e_branco.jpg", resultado["cinza"])
            print("\nSalvei como 'resultado_preto_e_branco.jpg'. 🎉")
