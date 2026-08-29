"""
The actual on-screen overlay: a transparent, click-through, always-on-top
window covering one monitor, with the crosshair painted at its center.
"""

from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt
from render import paint_crosshair


class CrosshairOverlay(QWidget):
    def __init__(self, config, screen=None):
        super().__init__()
        self.config = config

        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.WindowTransparentForInput  # let clicks pass through to the game
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)

        self.set_screen(screen or QApplication.primaryScreen())

    def set_screen(self, screen):
        """Move/resize the overlay to fully cover the given QScreen."""
        self.setGeometry(screen.geometry())

    def set_config(self, config):
        self.config = config
        self.update()

    def paintEvent(self, event):
        from PySide6.QtGui import QPainter
        painter = QPainter(self)
        cx = self.width() // 2
        cy = self.height() // 2
        paint_crosshair(painter, cx, cy, self.config)
