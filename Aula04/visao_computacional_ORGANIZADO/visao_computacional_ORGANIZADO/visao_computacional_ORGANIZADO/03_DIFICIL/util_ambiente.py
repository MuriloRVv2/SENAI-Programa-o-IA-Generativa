# ==============================================================================
#  util_ambiente.py  —  O "CONTROLE REMOTO UNIVERSAL" da nossa aula
# ------------------------------------------------------------------------------
#  Analogia: imagina que você tem uma TV (o seu código de visão computacional).
#  Mas existem dois tipos de tomada na parede: a tomada do Google Colab e a
#  tomada do seu computador (PyCharm/VSCode). Esse arquivo é o ADAPTADOR de
#  tomada universal: ele descobre sozinho onde você está e "encaixa" certinho.
#
#  Você NÃO precisa entender tudo aqui agora. Só precisa saber 3 funções:
#     - estou_no_colab()        -> True se você estiver no Google Colab
#     - mostrar_imagem(img)     -> mostra a imagem na tela (funciona nos dois!)
#     - escolher_arquivo()      -> abre uma janelinha pra você escolher um arquivo
# ==============================================================================

import cv2


def estou_no_colab():
    """Descobre se estamos rodando dentro do Google Colab."""
    try:
        import google.colab  # noqa: F401
        return True
    except ImportError:
        return False


def mostrar_imagem(imagem, titulo="Resultado"):
    """
    Mostra uma imagem na tela.

    Por que precisamos disso? Porque o comando normal do OpenCV
    (cv2.imshow) abre uma "janelinha" que SÓ funciona no seu computador.
    No Colab não existe janela! Então lá usamos outro jeito.
    Essa função resolve isso pra você automaticamente.
    """
    if estou_no_colab():
        # No Colab: o Google tem um comando especial pra mostrar imagem.
        from google.colab.patches import cv2_imshow
        cv2_imshow(imagem)
    else:
        # No computador: abrimos uma janela de verdade.
        cv2.imshow(titulo, imagem)
        print(">> Pressione qualquer tecla (com a janela selecionada) para fechar.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def escolher_arquivo():
    """
    Abre um seletor de arquivos para o aluno ESCOLHER a própria imagem/vídeo.

    Isso é o que permite testar com arquivos EXTERNOS (suas próprias fotos!).
    """
    if estou_no_colab():
        # No Colab aparece um botão "Escolher arquivos" na saída da célula.
        from google.colab import files
        print(">> Clique no botão abaixo e envie sua imagem do computador:")
        enviados = files.upload()
        # Retorna o nome do primeiro arquivo enviado.
        return list(enviados.keys())[0]
    else:
        # No computador abrimos uma janelinha do sistema operacional.
        from tkinter import Tk, filedialog
        Tk().withdraw()  # esconde a janela principal feia do tkinter
        caminho = filedialog.askopenfilename(
            title="Escolha uma imagem ou vídeo",
            filetypes=[("Imagens e vídeos", "*.jpg *.jpeg *.png *.bmp *.mp4 *.avi"),
                       ("Todos os arquivos", "*.*")]
        )
        return caminho


def webcam_disponivel():
    """
    No Colab NÃO dá pra usar a webcam do jeito tradicional (cv2.VideoCapture).
    Essa função avisa o aluno quando a webcam não está disponível.
    """
    return not estou_no_colab()
