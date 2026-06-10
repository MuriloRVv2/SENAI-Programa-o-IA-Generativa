#!/usr/bin/env python3
# ==============================================================================
#  🎨  VISÃO COMPUTACIONAL — Interface Gráfica Principal
#  Arquivo: app_gui.py
#
#  COMO RODAR:
#    python app_gui.py
#
#  DEPENDÊNCIAS:
#    pip install PyQt6 opencv-python numpy SpeechRecognition
# ==============================================================================

import sys
import os
import cv2
import numpy as np

# Garante que os módulos da aula sejam encontrados
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QStackedWidget, QScrollArea,
    QFrame, QGridLayout, QSizePolicy, QTextEdit, QProgressBar,
    QMessageBox, QSlider, QGroupBox,
)
from PyQt6.QtGui import (
    QPixmap, QImage, QFont, QColor, QPalette, QIcon,
    QPainter, QBrush, QPen, QLinearGradient,
)
from PyQt6.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QSize, QPropertyAnimation,
    QEasingCurve, QRect,
)

# ── Paleta de cores (pastel / vibrante, SEM tons escuros) ────────────────────
BG         = "#FFF8F0"        # fundo geral — creme quente
CARD_BG    = "#FFFFFF"        # cartões brancos
ACCENT1    = "#FF6B6B"        # coral — ação principal
ACCENT2    = "#4ECDC4"        # turquesa — secundário
ACCENT3    = "#FFE66D"        # amarelo — destaque/hover
ACCENT4    = "#A8E6CF"        # verde menta — sucesso
ACCENT5    = "#C3B1E1"        # lilás — STT
TEXT_DARK  = "#3D3D3D"        # texto principal
TEXT_MID   = "#7D7D7D"        # texto secundário
BORDER     = "#E8E0D8"        # bordas suaves

CARD_COLORS = [
    ("#FFE0E0", ACCENT1),  # Ex 1 — vermelho pastel
    ("#D8F5F3", ACCENT2),  # Ex 2 — turquesa pastel
    ("#FFF6CC", "#F0A500"), # Ex 3 — amarelo pastel
    ("#DCF5E8", "#3BAA6A"), # Ex 4 — verde pastel
    ("#EDE0F7", ACCENT5),  # Ex 5 — lilás pastel
]

EMOJIS = ["🖼️", "😊", "✨", "📸", "🎤"]

TITULOS = [
    "Primeira Imagem",
    "Detectar Rostos",
    "Filtros & Desenhos",
    "Edição de Fotos",
    "Fala → Texto",
]

DESCRICOES = [
    "Abre, converte pra\npreto e branco e\nredimensiona a imagem.",
    "Encontra rostos numa\nfoto usando o detetive\nHaar Cascade.",
    "Aplica filtros de\nborrão, bordas,\nnegativo e desenhos.",
    "Brilho, contraste,\ngirar, espelhar e\nrecortar a imagem.",
    "Grava sua voz e\nconverte em texto\nusando o Google STT.",
]


# ══════════════════════════════════════════════════════════════════════════════
#  UTILITÁRIOS
# ══════════════════════════════════════════════════════════════════════════════

def cv2_para_pixmap(imagem_bgr, max_w=800, max_h=500):
    """Converte imagem OpenCV (BGR) para QPixmap, respeitando tamanho máximo."""
    if imagem_bgr is None:
        return QPixmap()

    # Garante 3 canais
    if len(imagem_bgr.shape) == 2:
        imagem_bgr = cv2.cvtColor(imagem_bgr, cv2.COLOR_GRAY2BGR)

    h, w = imagem_bgr.shape[:2]
    escala = min(max_w / w, max_h / h, 1.0)
    if escala < 1.0:
        imagem_bgr = cv2.resize(imagem_bgr, (int(w * escala), int(h * escala)),
                                interpolation=cv2.INTER_AREA)

    rgb = cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2RGB)
    h2, w2, ch = rgb.shape
    qi = QImage(rgb.data, w2, h2, ch * w2, QImage.Format.Format_RGB888)
    return QPixmap.fromImage(qi)


def label_imagem(texto="Nenhuma imagem"):
    """Cria um QLabel para exibir imagem com estilo."""
    lb = QLabel(texto)
    lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lb.setMinimumSize(600, 380)
    lb.setStyleSheet(f"""
        QLabel {{
            background: {CARD_BG};
            border: 2.5px dashed {BORDER};
            border-radius: 16px;
            color: {TEXT_MID};
            font-size: 15px;
            font-family: 'Segoe UI', sans-serif;
        }}
    """)
    lb.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    return lb


# ══════════════════════════════════════════════════════════════════════════════
#  BOTÕES CUSTOMIZADOS
# ══════════════════════════════════════════════════════════════════════════════

def make_btn(texto, cor=ACCENT1, cor_texto="#FFFFFF", grande=False):
    btn = QPushButton(texto)
    tamanho = "14px" if grande else "12px"
    padding = "14px 28px" if grande else "10px 22px"
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {cor};
            color: {cor_texto};
            border: none;
            border-radius: 24px;
            font-size: {tamanho};
            font-weight: bold;
            font-family: 'Segoe UI', sans-serif;
            padding: {padding};
        }}
        QPushButton:hover {{
            background-color: {ACCENT3};
            color: {TEXT_DARK};
        }}
        QPushButton:pressed {{
            opacity: 0.85;
        }}
        QPushButton:disabled {{
            background-color: {BORDER};
            color: {TEXT_MID};
        }}
    """)
    return btn


# ══════════════════════════════════════════════════════════════════════════════
#  CARD DE MÓDULO (tela inicial)
# ══════════════════════════════════════════════════════════════════════════════

class ModuleCard(QFrame):
    clicked = pyqtSignal(int)

    def __init__(self, idx: int, parent=None):
        super().__init__(parent)
        self._idx = idx
        bg, accent = CARD_COLORS[idx]

        self.setFixedSize(200, 230)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._accent = accent
        self._bg = bg
        self._normal_style = f"""
            QFrame {{
                background: {bg};
                border-radius: 20px;
                border: 2.5px solid {BORDER};
            }}
        """
        self._hover_style = f"""
            QFrame {{
                background: {bg};
                border-radius: 20px;
                border: 3px solid {accent};
            }}
        """
        self.setStyleSheet(self._normal_style)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)

        emoji = QLabel(EMOJIS[idx])
        emoji.setAlignment(Qt.AlignmentFlag.AlignCenter)
        emoji.setStyleSheet("font-size: 48px; border: none; background: transparent;")

        num = QLabel(f"Exemplo {idx + 1}")
        num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        num.setStyleSheet(f"""
            font-size: 11px; font-weight: bold; color: {accent};
            border: none; background: transparent; letter-spacing: 1px;
        """)

        titulo = QLabel(TITULOS[idx])
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setWordWrap(True)
        titulo.setStyleSheet(f"""
            font-size: 14px; font-weight: bold; color: {TEXT_DARK};
            border: none; background: transparent;
        """)

        desc = QLabel(DESCRICOES[idx])
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet(f"""
            font-size: 11px; color: {TEXT_MID};
            border: none; background: transparent;
        """)

        for w in (emoji, num, titulo, desc):
            layout.addWidget(w)

    def enterEvent(self, e):
        self.setStyleSheet(self._hover_style)
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.setStyleSheet(self._normal_style)
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        self.clicked.emit(self._idx)
        super().mousePressEvent(e)


# ══════════════════════════════════════════════════════════════════════════════
#  TELA INICIAL (HomeScreen)
# ══════════════════════════════════════════════════════════════════════════════

class HomeScreen(QWidget):
    module_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {BG};")

        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        root.setSpacing(0)
        root.setContentsMargins(40, 40, 40, 40)

        # ── Cabeçalho ────────────────────────────────────────────────────────
        header = QLabel("🤖  Visão Computacional")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(f"""
            font-size: 34px; font-weight: bold; color: {TEXT_DARK};
            font-family: 'Segoe UI', sans-serif; letter-spacing: -0.5px;
            background: transparent;
        """)

        sub = QLabel("Escolha um exemplo abaixo para começar ✨")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"""
            font-size: 16px; color: {TEXT_MID};
            font-family: 'Segoe UI', sans-serif;
            background: transparent; margin-top: 4px;
        """)

        root.addWidget(header)
        root.addWidget(sub)
        root.addSpacing(36)

        # ── Grid de cards ─────────────────────────────────────────────────────
        grid = QWidget()
        grid.setStyleSheet("background: transparent;")
        grid_layout = QHBoxLayout(grid)
        grid_layout.setSpacing(20)
        grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for i in range(5):
            card = ModuleCard(i)
            card.clicked.connect(self.module_selected)
            grid_layout.addWidget(card)

        root.addWidget(grid)
        root.addSpacing(32)

        # ── Rodapé informativo ────────────────────────────────────────────────
        footer = QLabel("💡 Dica: todos os exemplos funcionam com arquivos externos — use suas próprias fotos!")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setWordWrap(True)
        footer.setStyleSheet(f"""
            font-size: 13px; color: {TEXT_MID};
            background: transparent; padding: 12px 20px;
        """)
        root.addWidget(footer)


# ══════════════════════════════════════════════════════════════════════════════
#  BARRA DE TÍTULO DAS TELAS DE MÓDULO
# ══════════════════════════════════════════════════════════════════════════════

class ModuleHeader(QWidget):
    back_clicked = pyqtSignal()

    def __init__(self, idx: int, parent=None):
        super().__init__(parent)
        _, accent = CARD_COLORS[idx]
        self.setStyleSheet(f"background: {CARD_BG}; border-bottom: 2px solid {BORDER};")
        self.setFixedHeight(72)

        h = QHBoxLayout(self)
        h.setContentsMargins(20, 0, 20, 0)

        btn_voltar = make_btn("← Voltar", ACCENT2)
        btn_voltar.setFixedWidth(110)
        btn_voltar.clicked.connect(self.back_clicked)

        emoji_lb = QLabel(EMOJIS[idx])
        emoji_lb.setStyleSheet("font-size: 28px; background: transparent;")

        titulo = QLabel(f"Exemplo {idx + 1}  —  {TITULOS[idx]}")
        titulo.setStyleSheet(f"""
            font-size: 18px; font-weight: bold; color: {TEXT_DARK};
            background: transparent; font-family: 'Segoe UI', sans-serif;
        """)

        h.addWidget(btn_voltar)
        h.addSpacing(16)
        h.addWidget(emoji_lb)
        h.addWidget(titulo)
        h.addStretch()


# ══════════════════════════════════════════════════════════════════════════════
#  MÓDULO 1 — Primeira Imagem
# ══════════════════════════════════════════════════════════════════════════════

def _carregar_modulo(nome_arquivo, alias):
    """Carrega dinamicamente um módulo a partir do diretório do script."""
    import importlib.util
    base = os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location(
        alias, os.path.join(base, nome_arquivo))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class Modulo1(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {BG};")
        self._resultados = None

        root = QVBoxLayout(self)
        root.setContentsMargins(30, 24, 30, 24)
        root.setSpacing(16)

        # Painel de botões
        btn_bar = QHBoxLayout()
        self.btn_abrir = make_btn("📂  Escolher imagem", ACCENT1, grande=True)
        self.btn_abrir.clicked.connect(self._abrir)
        self.btn_salvar = make_btn("💾  Salvar preto e branco", ACCENT2)
        self.btn_salvar.setEnabled(False)
        self.btn_salvar.clicked.connect(self._salvar)
        btn_bar.addWidget(self.btn_abrir)
        btn_bar.addSpacing(12)
        btn_bar.addWidget(self.btn_salvar)
        btn_bar.addStretch()
        root.addLayout(btn_bar)

        # Status
        self.status = QLabel("Escolha uma imagem para começar.")
        self.status.setStyleSheet(f"color: {TEXT_MID}; font-size: 13px; background: transparent;")
        root.addWidget(self.status)

        # Grid de imagens: Original | Cinza | Metade
        grid = QGridLayout()
        grid.setSpacing(14)
        self.lb_orig  = self._make_img_slot("Original",         CARD_COLORS[0][1])
        self.lb_cinza = self._make_img_slot("Preto e Branco",   "#555555")
        self.lb_menor = self._make_img_slot("Metade do Tamanho", ACCENT2)

        for col, (titulo, lb) in enumerate([
            ("🖼️  Original",          self.lb_orig),
            ("⬛  Preto & Branco",    self.lb_cinza),
            ("🔍  Metade do Tamanho", self.lb_menor),
        ]):
            wrapper = QVBoxLayout()
            t = QLabel(titulo)
            t.setAlignment(Qt.AlignmentFlag.AlignCenter)
            t.setStyleSheet(f"font-weight: bold; font-size: 13px; color: {TEXT_DARK}; background: transparent;")
            wrapper.addWidget(t)
            wrapper.addWidget(lb)
            cell = QWidget()
            cell.setStyleSheet("background: transparent;")
            cell.setLayout(wrapper)
            grid.addWidget(cell, 0, col)

        root.addLayout(grid)

    def _make_img_slot(self, hint, accent):
        lb = QLabel(f"📷\n{hint}")
        lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lb.setMinimumSize(300, 250)
        lb.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lb.setStyleSheet(f"""
            QLabel {{
                background: {CARD_BG};
                border: 2.5px dashed {accent}55;
                border-radius: 14px;
                color: {TEXT_MID};
                font-size: 13px;
            }}
        """)
        return lb

    def _abrir(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Escolha uma imagem", "",
            "Imagens (*.jpg *.jpeg *.png *.bmp);;Todos (*.*)"
        )
        if not caminho:
            return
        self.status.setText("⏳ Processando...")
        QApplication.processEvents()

        # FIX: removida importação inválida de 'o1_primeira_imagem_logic';
        #      carregamento feito exclusivamente via helper _carregar_modulo.
        m = _carregar_modulo("01_primeira_imagem.py", "m01")

        res = m.processar_imagem(caminho)
        if res is None:
            self.status.setText("❌ Não consegui abrir essa imagem.")
            return

        self._resultados = res
        self.lb_orig.setPixmap(cv2_para_pixmap(res["original"],  300, 250))
        self.lb_cinza.setPixmap(cv2_para_pixmap(res["cinza"],    300, 250))
        self.lb_menor.setPixmap(cv2_para_pixmap(res["metade"],   300, 250))
        w, h = res["largura"], res["altura"]
        self.status.setText(f"✅  Imagem carregada!  {w} × {h} px  —  pronto para salvar.")
        self.btn_salvar.setEnabled(True)

    def _salvar(self):
        if self._resultados is None:
            return
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar preto e branco", "resultado_preto_e_branco.jpg",
            "Imagem JPEG (*.jpg);;PNG (*.png)"
        )
        if caminho:
            cv2.imwrite(caminho, self._resultados["cinza"])
            self.status.setText(f"💾  Salvo em: {caminho}")


# ══════════════════════════════════════════════════════════════════════════════
#  MÓDULO 2 — Detectar Rostos
# ══════════════════════════════════════════════════════════════════════════════

class WebcamThread(QThread):
    frame_ready = pyqtSignal(np.ndarray, int)
    error = pyqtSignal(str)

    def __init__(self, detector):
        super().__init__()
        self._running = True
        self._detector = detector

    def run(self):
        m = _carregar_modulo("02_deteccao_rosto_haar.py", "m02_wcam")

        camera = m.abrir_camera()
        if camera is None:
            self.error.emit("❌ Não foi possível abrir a webcam.")
            return
        while self._running:
            ok, quadro = camera.read()
            if not ok:
                break
            anotado, n = m.detectar_rostos(quadro, self._detector)
            self.frame_ready.emit(anotado, n)
        camera.release()

    def parar(self):
        self._running = False
        self.quit()
        self.wait()


class Modulo2(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {BG};")
        self._detector = None
        self._m02 = None          # módulo carregado, reutilizado em _modo_foto
        self._webcam_thread = None

        root = QVBoxLayout(self)
        root.setContentsMargins(30, 24, 30, 24)
        root.setSpacing(16)

        # Botões
        btn_bar = QHBoxLayout()
        self.btn_foto   = make_btn("📂  Foto com pessoas",  ACCENT1, grande=True)
        self.btn_webcam = make_btn("📷  Webcam ao vivo",    ACCENT2, grande=True)
        self.btn_salvar = make_btn("💾  Salvar resultado",  ACCENT4, cor_texto=TEXT_DARK)
        self.btn_salvar.setEnabled(False)
        self.btn_foto.clicked.connect(self._modo_foto)
        self.btn_webcam.clicked.connect(self._toggle_webcam)
        self.btn_salvar.clicked.connect(self._salvar)
        for b in (self.btn_foto, self.btn_webcam, self.btn_salvar):
            btn_bar.addWidget(b)
        btn_bar.addStretch()
        root.addLayout(btn_bar)

        self.status = QLabel("Escolha um modo para começar.")
        self.status.setStyleSheet(f"color: {TEXT_MID}; font-size: 13px; background: transparent;")
        root.addWidget(self.status)

        # Área de imagem
        self.lb_img = label_imagem("😊  Nenhuma imagem ainda\n\nCarregue uma foto ou ligue a webcam")
        root.addWidget(self.lb_img)

        self._ultima_imagem = None

    def _get_detector(self):
        """Carrega o módulo e o detector uma única vez."""
        if self._detector is None:
            self._m02 = _carregar_modulo("02_deteccao_rosto_haar.py", "m02")
            self._detector = self._m02.carregar_detector()
        return self._detector

    def _modo_foto(self):
        self._parar_webcam()
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Escolha uma foto com pessoas", "",
            "Imagens (*.jpg *.jpeg *.png *.bmp);;Todos (*.*)"
        )
        if not caminho:
            return
        self.status.setText("⏳ Detectando rostos...")
        QApplication.processEvents()

        det = self._get_detector()
        # FIX: reutiliza self._m02 já carregado; não recarrega com alias diferente
        res = self._m02.processar_imagem_rostos(caminho, det)
        if res is None:
            self.status.setText("❌ Não consegui abrir essa imagem.")
            return

        self._ultima_imagem = res["anotada"]
        self.lb_img.setPixmap(cv2_para_pixmap(res["anotada"], 800, 480))
        n = res["n_rostos"]
        emoji = "😊" if n > 0 else "🤔"
        self.status.setText(f"{emoji}  Encontrei {n} rosto(s) na foto!")
        self.btn_salvar.setEnabled(True)

    def _toggle_webcam(self):
        if self._webcam_thread and self._webcam_thread.isRunning():
            self._parar_webcam()
        else:
            self._iniciar_webcam()

    def _iniciar_webcam(self):
        det = self._get_detector()
        self._webcam_thread = WebcamThread(det)
        self._webcam_thread.frame_ready.connect(self._on_frame)
        self._webcam_thread.error.connect(lambda msg: self.status.setText(msg))
        self._webcam_thread.start()
        self.btn_webcam.setText("⏹️  Parar webcam")
        self.status.setText("📷  Webcam ao vivo — clique em 'Parar' para encerrar.")

    def _parar_webcam(self):
        if self._webcam_thread:
            self._webcam_thread.parar()
            self._webcam_thread = None
        self.btn_webcam.setText("📷  Webcam ao vivo")

    def _on_frame(self, frame, n):
        self._ultima_imagem = frame.copy()
        self.lb_img.setPixmap(cv2_para_pixmap(frame, 800, 480))
        self.status.setText(f"📷  Ao vivo — {n} rosto(s) detectado(s) agora")
        self.btn_salvar.setEnabled(True)

    def _salvar(self):
        if self._ultima_imagem is None:
            return
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar resultado", "rostos_detectados.jpg",
            "Imagem JPEG (*.jpg);;PNG (*.png)"
        )
        if caminho:
            cv2.imwrite(caminho, self._ultima_imagem)
            self.status.setText(f"💾  Salvo em: {caminho}")

    def hideEvent(self, e):
        self._parar_webcam()
        super().hideEvent(e)


# ══════════════════════════════════════════════════════════════════════════════
#  MÓDULO 3 — Filtros & Desenhos
# ══════════════════════════════════════════════════════════════════════════════

FILTROS_INFO = [
    ("original",  "🖼️  Original"),
    ("borrada",   "🌫️  Borrado"),
    ("bordas",    "✏️  Bordas"),
    ("negativo",  "🔄  Negativo"),
    ("desenhada", "🎨  Com Desenhos"),
]


class Modulo3(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {BG};")
        self._resultados = None

        root = QVBoxLayout(self)
        root.setContentsMargins(30, 24, 30, 24)
        root.setSpacing(14)

        btn_bar = QHBoxLayout()
        self.btn_abrir  = make_btn("📂  Escolher imagem", ACCENT1, grande=True)
        self.btn_salvar = make_btn("💾  Salvar resultado", ACCENT2)
        self.btn_salvar.setEnabled(False)
        self.btn_abrir.clicked.connect(self._abrir)
        self.btn_salvar.clicked.connect(self._salvar)
        btn_bar.addWidget(self.btn_abrir)
        btn_bar.addSpacing(12)
        btn_bar.addWidget(self.btn_salvar)
        btn_bar.addStretch()
        root.addLayout(btn_bar)

        self.status = QLabel("Escolha uma imagem para ver os filtros.")
        self.status.setStyleSheet(f"color: {TEXT_MID}; font-size: 13px; background: transparent;")
        root.addWidget(self.status)

        # Seletor de filtro
        sel_bar = QHBoxLayout()
        sel_bar.setSpacing(10)
        self._btns_filtro = []
        for key, label in FILTROS_INFO:
            b = QPushButton(label)
            b.setCheckable(True)
            b.setStyleSheet(f"""
                QPushButton {{
                    background: {CARD_BG};
                    color: {TEXT_MID};
                    border: 2px solid {BORDER};
                    border-radius: 20px;
                    padding: 8px 14px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                QPushButton:checked {{
                    background: {ACCENT3};
                    color: {TEXT_DARK};
                    border: 2px solid {ACCENT1};
                }}
                QPushButton:hover:!checked {{
                    background: #FFF0E0;
                }}
            """)
            b.clicked.connect(lambda _, k=key: self._mostrar_filtro(k))
            self._btns_filtro.append((key, b))
            sel_bar.addWidget(b)
        sel_bar.addStretch()
        root.addLayout(sel_bar)

        self.lb_img = label_imagem("✨  Filtros aparecerão aqui\n\nCarregue uma imagem primeiro")
        root.addWidget(self.lb_img)

        self._filtro_atual = "original"

    def _abrir(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Escolha uma imagem", "",
            "Imagens (*.jpg *.jpeg *.png *.bmp);;Todos (*.*)"
        )
        if not caminho:
            return
        self.status.setText("⏳ Aplicando filtros...")
        QApplication.processEvents()

        m = _carregar_modulo("03_filtros_desenhos.py", "m03")

        self._resultados = m.processar_imagem_filtros(caminho)
        if self._resultados is None:
            self.status.setText("❌ Não consegui abrir essa imagem.")
            return

        self._mostrar_filtro("original")
        self.btn_salvar.setEnabled(True)
        self.status.setText("✅  Filtros aplicados! Clique nos botões acima para trocar.")

    def _mostrar_filtro(self, key):
        if self._resultados is None:
            return
        self._filtro_atual = key
        img = self._resultados.get(key)
        if img is not None:
            self.lb_img.setPixmap(cv2_para_pixmap(img, 800, 480))
        # Atualiza estado visual dos botões
        for k, b in self._btns_filtro:
            b.setChecked(k == key)

    def _salvar(self):
        if self._resultados is None:
            return
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar imagem", "imagem_com_filtros.jpg",
            "Imagem JPEG (*.jpg);;PNG (*.png)"
        )
        if caminho:
            cv2.imwrite(caminho, self._resultados[self._filtro_atual])
            self.status.setText(f"💾  Salvo em: {caminho}")


# ══════════════════════════════════════════════════════════════════════════════
#  MÓDULO 4 — Edição de Fotos
# ══════════════════════════════════════════════════════════════════════════════

EDICOES_INFO = [
    ("original",  "🖼️  Original"),
    ("ajustada",  "☀️  Brilho+Contraste"),
    ("espelhada", "↔️  Espelhada"),
    ("girada",    "🔃  Girada 90°"),
    ("recorte",   "✂️  Recorte Central"),
]


class Modulo4(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {BG};")
        self._resultados = None
        self._edicao_atual = "original"

        root = QVBoxLayout(self)
        root.setContentsMargins(30, 24, 30, 24)
        root.setSpacing(14)

        btn_bar = QHBoxLayout()
        self.btn_abrir  = make_btn("📂  Escolher imagem", CARD_COLORS[3][1], cor_texto="#FFF", grande=True)
        self.btn_salvar = make_btn("💾  Salvar", ACCENT2)
        self.btn_salvar.setEnabled(False)
        self.btn_abrir.clicked.connect(self._abrir)
        self.btn_salvar.clicked.connect(self._salvar)
        btn_bar.addWidget(self.btn_abrir)
        btn_bar.addSpacing(12)
        btn_bar.addWidget(self.btn_salvar)
        btn_bar.addStretch()
        root.addLayout(btn_bar)

        self.status = QLabel("Escolha uma imagem para editar.")
        self.status.setStyleSheet(f"color: {TEXT_MID}; font-size: 13px; background: transparent;")
        root.addWidget(self.status)

        # Seletor
        sel_bar = QHBoxLayout()
        sel_bar.setSpacing(10)
        self._btns_ed = []
        _, accent = CARD_COLORS[3]
        for key, label in EDICOES_INFO:
            b = QPushButton(label)
            b.setCheckable(True)
            b.setStyleSheet(f"""
                QPushButton {{
                    background: {CARD_BG};
                    color: {TEXT_MID};
                    border: 2px solid {BORDER};
                    border-radius: 20px;
                    padding: 8px 14px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                QPushButton:checked {{
                    background: {ACCENT4};
                    color: {TEXT_DARK};
                    border: 2px solid {accent};
                }}
                QPushButton:hover:!checked {{ background: #E8F8EF; }}
            """)
            b.clicked.connect(lambda _, k=key: self._mostrar_edicao(k))
            self._btns_ed.append((key, b))
            sel_bar.addWidget(b)
        sel_bar.addStretch()
        root.addLayout(sel_bar)

        self.lb_img = label_imagem("📸  Edições aparecerão aqui\n\nCarregue uma imagem primeiro")
        root.addWidget(self.lb_img)

    def _abrir(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Escolha uma imagem", "",
            "Imagens (*.jpg *.jpeg *.png *.bmp);;Todos (*.*)"
        )
        if not caminho:
            return
        self.status.setText("⏳ Aplicando edições...")
        QApplication.processEvents()

        m = _carregar_modulo("04_opencv_edicao_de_fotos.py", "m04")

        self._resultados = m.processar_edicao_fotos(caminho)
        if self._resultados is None:
            self.status.setText("❌ Não consegui abrir essa imagem.")
            return

        self._mostrar_edicao("original")
        self.btn_salvar.setEnabled(True)
        self.status.setText("✅  Edições prontas! Clique nos botões para comparar.")

    def _mostrar_edicao(self, key):
        if self._resultados is None:
            return
        self._edicao_atual = key
        img = self._resultados.get(key)
        if img is not None:
            self.lb_img.setPixmap(cv2_para_pixmap(img, 800, 480))
        for k, b in self._btns_ed:
            b.setChecked(k == key)

    def _salvar(self):
        if self._resultados is None:
            return
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar imagem", "opencv_editada.jpg",
            "Imagem JPEG (*.jpg);;PNG (*.png)"
        )
        if caminho:
            cv2.imwrite(caminho, self._resultados[self._edicao_atual])
            self.status.setText(f"💾  Salvo em: {caminho}")


# ══════════════════════════════════════════════════════════════════════════════
#  MÓDULO 5 — Speech to Text
# ══════════════════════════════════════════════════════════════════════════════

class STTThread(QThread):
    status_update  = pyqtSignal(str)
    resultado      = pyqtSignal(str)

    def __init__(self, modo, caminho=None):
        super().__init__()
        self._modo    = modo      # "mic" ou "arquivo"
        self._caminho = caminho

    def run(self):
        import threading

        m = _carregar_modulo("05_stt_fala_virou_texto.py", "m05")

        if self._modo == "mic":
            resultado = m.transcrever_microfone(
                callback_status=self.status_update.emit,
                callback_resultado=self.resultado.emit,
            )
        else:
            resultado = m.transcrever_arquivo_audio(
                self._caminho,
                callback_resultado=self.resultado.emit,
            )

        # FIX: só chama .join() se o retorno for de fato uma Thread
        if isinstance(resultado, threading.Thread):
            resultado.join()


class Modulo5(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {BG};")
        self._thread = None

        root = QVBoxLayout(self)
        root.setContentsMargins(30, 24, 30, 24)
        root.setSpacing(16)

        # Card central
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {CARD_BG};
                border-radius: 20px;
                border: 2px solid {BORDER};
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 32, 36, 32)
        card_layout.setSpacing(20)

        # Ícone
        icon = QLabel("🎤")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 56px; background: transparent; border: none;")
        card_layout.addWidget(icon)

        # Título
        titulo = QLabel("Converta sua voz em texto!")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet(f"""
            font-size: 20px; font-weight: bold; color: {TEXT_DARK};
            background: transparent; border: none;
        """)
        card_layout.addWidget(titulo)

        # Botões modo
        btns = QHBoxLayout()
        self.btn_mic     = make_btn("🎤  Usar microfone",       ACCENT5, cor_texto=TEXT_DARK, grande=True)
        self.btn_arquivo = make_btn("📁  Carregar arquivo .wav", ACCENT2, grande=True)
        self.btn_mic.clicked.connect(self._usar_microfone)
        self.btn_arquivo.clicked.connect(self._usar_arquivo)
        btns.addWidget(self.btn_mic)
        btns.addSpacing(16)
        btns.addWidget(self.btn_arquivo)
        card_layout.addLayout(btns)

        # Status / progresso
        self.status = QLabel("Escolha um modo para começar.")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet(f"color: {TEXT_MID}; font-size: 13px; background: transparent; border: none;")
        card_layout.addWidget(self.status)

        # Resultado
        result_label = QLabel("📝  Transcrição:")
        result_label.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {TEXT_DARK}; background: transparent; border: none;")
        card_layout.addWidget(result_label)

        self.txt_resultado = QTextEdit()
        self.txt_resultado.setReadOnly(True)
        self.txt_resultado.setMinimumHeight(120)
        self.txt_resultado.setStyleSheet(f"""
            QTextEdit {{
                background: {BG};
                border: 2px solid {BORDER};
                border-radius: 12px;
                font-size: 16px;
                color: {TEXT_DARK};
                padding: 12px;
                font-family: 'Segoe UI', sans-serif;
            }}
        """)
        card_layout.addWidget(self.txt_resultado)

        # Botão copiar
        self.btn_copiar = make_btn("📋  Copiar texto", ACCENT4, cor_texto=TEXT_DARK)
        self.btn_copiar.setEnabled(False)
        self.btn_copiar.clicked.connect(self._copiar)
        card_layout.addWidget(self.btn_copiar, alignment=Qt.AlignmentFlag.AlignRight)

        root.addWidget(card)
        root.addStretch()

    def _usar_microfone(self):
        self._iniciar_stt("mic")

    def _usar_arquivo(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Escolha um arquivo de áudio", "",
            "Áudio WAV (*.wav);;Todos (*.*)"
        )
        if caminho:
            self._iniciar_stt("arquivo", caminho)

    def _iniciar_stt(self, modo, caminho=None):
        self.btn_copiar.setEnabled(False)
        self.txt_resultado.clear()
        self._thread = STTThread(modo, caminho)
        self._thread.status_update.connect(self.status.setText)
        self._thread.resultado.connect(self._on_resultado)
        self._thread.start()
        self.status.setText("⏳ Iniciando...")

    def _on_resultado(self, texto):
        self.txt_resultado.setPlainText(texto)
        self.status.setText("✅  Pronto!")
        self.btn_copiar.setEnabled(True)

    def _copiar(self):
        QApplication.clipboard().setText(self.txt_resultado.toPlainText())
        self.btn_copiar.setText("✅  Copiado!")
        QTimer.singleShot(2000, lambda: self.btn_copiar.setText("📋  Copiar texto"))


# ══════════════════════════════════════════════════════════════════════════════
#  JANELA PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🤖  Visão Computacional — Aula Interativa")
        self.setMinimumSize(1100, 720)
        self.setStyleSheet(f"background: {BG};")

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Stack principal
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background: {BG};")

        # Tela 0: home
        self.home = HomeScreen()
        self.home.module_selected.connect(self._ir_para_modulo)
        self.stack.addWidget(self.home)

        # Módulos 1-5
        self._modulos_widgets = []
        modulo_classes = [Modulo1, Modulo2, Modulo3, Modulo4, Modulo5]
        for idx, cls in enumerate(modulo_classes):
            wrapper = QWidget()
            wrapper.setStyleSheet(f"background: {BG};")
            vbox = QVBoxLayout(wrapper)
            vbox.setContentsMargins(0, 0, 0, 0)
            vbox.setSpacing(0)

            header = ModuleHeader(idx)
            header.back_clicked.connect(self._voltar_home)
            vbox.addWidget(header)

            conteudo = cls()
            scroll = QScrollArea()
            scroll.setWidget(conteudo)
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet(f"QScrollArea {{ border: none; background: {BG}; }}")
            vbox.addWidget(scroll)

            self.stack.addWidget(wrapper)
            self._modulos_widgets.append(wrapper)

        root.addWidget(self.stack)

    def _ir_para_modulo(self, idx: int):
        self.stack.setCurrentIndex(idx + 1)

    def _voltar_home(self):
        self.stack.setCurrentIndex(0)


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Paleta global clara
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window,          QColor(BG))
    palette.setColor(QPalette.ColorRole.WindowText,      QColor(TEXT_DARK))
    palette.setColor(QPalette.ColorRole.Base,            QColor(CARD_BG))
    palette.setColor(QPalette.ColorRole.AlternateBase,   QColor(BG))
    palette.setColor(QPalette.ColorRole.Text,            QColor(TEXT_DARK))
    palette.setColor(QPalette.ColorRole.Button,          QColor(CARD_BG))
    palette.setColor(QPalette.ColorRole.ButtonText,      QColor(TEXT_DARK))
    palette.setColor(QPalette.ColorRole.Highlight,       QColor(ACCENT1))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(palette)

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()