# ==============================================================================
#  util_ambiente.py  —  O "CONTROLE REMOTO UNIVERSAL" da nossa aula
# ------------------------------------------------------------------------------
#  Versão atualizada com suporte a PyQt6 e integração com a interface gráfica.
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
    Mostra uma imagem na tela. Se PyQt6 estiver disponível, exibe via Qt.
    Caso contrário, usa cv2.imshow (só funciona no computador local).
    """
    if estou_no_colab():
        from google.colab.patches import cv2_imshow
        cv2_imshow(imagem)
    else:
        cv2.imshow(titulo, imagem)
        print(">> Pressione qualquer tecla (com a janela selecionada) para fechar.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def escolher_arquivo(parent=None, tipos=None):
    """
    Abre um seletor de arquivos. Usa PyQt6 se disponível, senão tkinter.
    """
    if estou_no_colab():
        from google.colab import files
        print(">> Clique no botão abaixo e envie sua imagem do computador:")
        enviados = files.upload()
        return list(enviados.keys())[0] if enviados else ""

    # Tenta PyQt6 primeiro
    try:
        from PyQt6.QtWidgets import QApplication, QFileDialog
        import sys
        app = QApplication.instance() or QApplication(sys.argv)
        filtro = tipos or "Imagens (*.jpg *.jpeg *.png *.bmp);;Todos os arquivos (*.*)"
        caminho, _ = QFileDialog.getOpenFileName(parent, "Escolha um arquivo", "", filtro)
        return caminho
    except ImportError:
        pass

    # Fallback: tkinter
    try:
        from tkinter import Tk, filedialog
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        root.lift()
        root.update()
        caminho = filedialog.askopenfilename(
            parent=root,
            title="Escolha uma imagem ou vídeo",
            filetypes=[("Imagens e vídeos", "*.jpg *.jpeg *.png *.bmp *.mp4 *.avi"),
                       ("Todos os arquivos", "*.*")]
        )
        root.destroy()
        return caminho
    except Exception:
        return input("Caminho do arquivo: ").strip().strip('"').strip("'")


def webcam_disponivel():
    """No Colab NÃO dá pra usar a webcam do jeito tradicional."""
    return not estou_no_colab()
