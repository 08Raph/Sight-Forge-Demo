"""
Shared crosshair drawing routine.

Both the fullscreen game overlay (overlay.py) and the small preview panel
inside the control window (control_panel.py) call this same function, so
what you see in the preview is exactly what gets drawn on screen.
"""

from PySide6.QtGui import QPainter, QColor, QPen, QBrush
from PySide6.QtCore import Qt, QPoint


def _rgba(hex_str, opacity_pct):
    c = QColor(hex_str)
    c.setAlphaF(max(0.0, min(1.0, opacity_pct / 100)))
    return c


def paint_crosshair(painter: QPainter, cx: int, cy: int, c: dict):
    """Paint the crosshair described by config dict `c`, centered at (cx, cy)."""
    painter.save()
    painter.setRenderHint(QPainter.Antialiasing)
    painter.translate(cx, cy)

    rotation = c.get("rotation", 0)
    if rotation:
        painter.rotate(rotation)

    color = _rgba(c.get("color", "#39ff14"), c.get("opacity", 100))
    outline_color = _rgba(c.get("outlineColor", "#000000"), c.get("outlineOpacity", 100))

    gap = c.get("gap", 3)
    length = c.get("length", 10)
    thickness = c.get("thickness", 2)
    outline_on = c.get("outlineEnabled", True)
    outline_width = c.get("outlineWidth", 1)

    lines = []
    if not c.get("tShape", False):
        lines.append((QPoint(0, -gap), QPoint(0, -gap - length)))   # top
    lines.append((QPoint(0, gap), QPoint(0, gap + length)))         # bottom
    lines.append((QPoint(-gap, 0), QPoint(-gap - length, 0)))       # left
    lines.append((QPoint(gap, 0), QPoint(gap + length, 0)))         # right

    if c.get("crossEnabled", True):
        if outline_on:
            pen = QPen(outline_color, thickness + outline_width * 2)
            pen.setCapStyle(Qt.FlatCap)
            painter.setPen(pen)
            for p1, p2 in lines:
                painter.drawLine(p1, p2)

        pen = QPen(color, thickness)
        pen.setCapStyle(Qt.FlatCap)
        painter.setPen(pen)
        for p1, p2 in lines:
            painter.drawLine(p1, p2)

    if c.get("circleEnabled", False):
        r = c.get("circleRadius", 20)
        circle_thickness = c.get("circleThickness", 1)
        painter.setBrush(Qt.NoBrush)

        if outline_on:
            pen = QPen(outline_color, circle_thickness + outline_width * 2)
            painter.setPen(pen)
            painter.drawEllipse(QPoint(0, 0), r, r)

        pen = QPen(color, circle_thickness)
        painter.setPen(pen)
        painter.drawEllipse(QPoint(0, 0), r, r)

    if c.get("centerDot", False):
        dot_r = c.get("dotSize", 2) / 2
        dot_color = _rgba(c.get("color", "#39ff14"), c.get("dotOpacity", 100))

        if outline_on:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(outline_color))
            painter.drawEllipse(QPoint(0, 0), dot_r + outline_width, dot_r + outline_width)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(dot_color))
        painter.drawEllipse(QPoint(0, 0), dot_r, dot_r)

    painter.restore()
