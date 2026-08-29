"""
The control panel: a normal (non-overlay) window with a live preview plus
every slider/toggle needed to design a crosshair. Every change fires
`configChanged`, which main.py wires straight to the fullscreen overlay, so
edits show up on screen instantly.
"""

import copy

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QCheckBox, QPushButton,
    QColorDialog, QScrollArea, QGridLayout, QLineEdit, QGroupBox, QListWidget,
    QListWidgetItem, QFileDialog, QMessageBox, QComboBox
)
from PySide6.QtGui import QPainter, QColor, QFont, QDesktopServices
from PySide6.QtCore import Qt, Signal, QUrl

from render import paint_crosshair
import presets as presets_mod

SWATCHES = ["#39ff14", "#ffffff", "#ff4b5c", "#3fe0d0", "#ffd400", "#ff7a1a", "#c86bff", "#ff69d0"]

# Full paid version's checkout link -- shown as a "Get the full version"
# button in the panel. Change/remove this if the product moves.
BUY_URL = "https://sightforge.lemonsqueezy.com/checkout/buy/f9a49dd7-5ba4-4d8f-a3ba-b229ed340022"

# Community Discord -- shown as a button in the panel and in the tray menu.
DISCORD_URL = "https://discord.gg/Ukcka2mqNr"

DARK_QSS = """
QWidget { background-color: #0B0E13; color: #E9EDF2; font-family: 'Segoe UI', sans-serif; }
QGroupBox {
    border: 1px solid #232A35; border-radius: 6px; margin-top: 14px;
    font-weight: 600; letter-spacing: 0.5px; padding-top: 6px;
}
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 6px; color: #FF7A1A; }
QPushButton {
    background-color: #1A2029; border: 1px solid #232A35; border-radius: 4px;
    padding: 7px 12px; color: #E9EDF2;
}
QPushButton:hover { background-color: #20272F; border-color: #3a4353; }
QPushButton#primary { background-color: #FF7A1A; color: #1a0d00; font-weight: 600; border: none; }
QPushButton#danger { color: #FF4B5C; }
QSlider::groove:horizontal { height: 4px; background: #232A35; border-radius: 2px; }
QSlider::handle:horizontal {
    background: #FF7A1A; width: 14px; height: 14px; margin: -6px 0; border-radius: 7px;
}
QCheckBox { spacing: 8px; }
QLineEdit {
    background-color: #1A2029; border: 1px solid #232A35; border-radius: 4px;
    padding: 6px 8px; color: #E9EDF2;
}
QListWidget { background-color: #12161D; border: 1px solid #232A35; border-radius: 4px; }
QScrollArea { border: none; }
QLabel#hint { color: #7C8698; font-size: 11px; }
QLabel#title { color: #E9EDF2; font-size: 18px; font-weight: 700; letter-spacing: 1px; }
"""


class PreviewWidget(QWidget):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setMinimumHeight(160)
        self.setStyleSheet("background-color: #14181f; border: 1px solid #232A35; border-radius: 4px;")

    def set_config(self, config):
        self.config = config
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        paint_crosshair(painter, self.width() // 2, self.height() // 2, self.config)


def _row(widget_left, widget_right):
    row = QHBoxLayout()
    row.addWidget(widget_left)
    row.addWidget(widget_right)
    return row


class ControlPanel(QWidget):
    configChanged = Signal(dict)
    toggleOverlayRequested = Signal()
    screenChangeRequested = Signal(int)
    quitRequested = Signal()

    def __init__(self, config, screens):
        super().__init__()
        self.setWindowTitle("SightForge Demo — Desktop")
        self.resize(430, 780)
        self.setStyleSheet(DARK_QSS)

        self.config = copy.deepcopy(config)

        outer = QVBoxLayout(self)
        outer.setSpacing(10)

        title = QLabel("CROSSHAIR STUDIO")
        title.setObjectName("title")
        outer.addWidget(title)

        links_row = QHBoxLayout()
        buy_btn = QPushButton("Get the full version →")
        buy_btn.setObjectName("primary")
        buy_btn.setToolTip(BUY_URL)
        buy_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(BUY_URL)))
        links_row.addWidget(buy_btn)

        discord_btn = QPushButton("Join the Discord")
        discord_btn.setToolTip(DISCORD_URL)
        discord_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(DISCORD_URL)))
        links_row.addWidget(discord_btn)
        outer.addLayout(links_row)

        self.preview = PreviewWidget(self.config)
        outer.addWidget(self.preview)

        top_btns = QHBoxLayout()
        self.toggle_btn = QPushButton("Hide Overlay")
        self.toggle_btn.clicked.connect(self.toggleOverlayRequested.emit)
        quit_btn = QPushButton("Quit App")
        quit_btn.setObjectName("danger")
        quit_btn.clicked.connect(self.quitRequested.emit)
        top_btns.addWidget(self.toggle_btn)
        top_btns.addWidget(quit_btn)
        outer.addLayout(top_btns)

        if len(screens) > 1:
            screen_row = QHBoxLayout()
            screen_row.addWidget(QLabel("Overlay monitor:"))
            self.screen_combo = QComboBox()
            for i, s in enumerate(screens):
                self.screen_combo.addItem(f"Screen {i+1} ({s.geometry().width()}x{s.geometry().height()})")
            self.screen_combo.currentIndexChanged.connect(self.screenChangeRequested.emit)
            screen_row.addWidget(self.screen_combo)
            outer.addLayout(screen_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.form = QVBoxLayout(content)
        self.form.setSpacing(12)
        scroll.setWidget(content)
        outer.addWidget(scroll, stretch=1)

        self._build_presets_group()
        self._build_shape_group()
        self._build_color_group()
        self._build_lines_group()
        self._build_dot_group()
        self._build_circle_group()
        self._build_outline_group()
        self._build_save_group()
        self._build_import_export_group()

        self.form.addStretch(1)

    # ---------------- helpers ----------------

    def _emit_change(self):
        self.preview.set_config(self.config)
        self.configChanged.emit(self.config)

    def _add_group(self, title):
        box = QGroupBox(title)
        layout = QVBoxLayout(box)
        layout.setSpacing(10)
        self.form.addWidget(box)
        return layout

    def _slider_row(self, layout, label_text, key, minv, maxv, suffix=""):
        row = QVBoxLayout()
        label_row = QHBoxLayout()
        label = QLabel(label_text)
        value_label = QLabel(f"{self.config.get(key, minv)}{suffix}")
        value_label.setAlignment(Qt.AlignRight)
        label_row.addWidget(label)
        label_row.addWidget(value_label)
        row.addLayout(label_row)

        slider = QSlider(Qt.Horizontal)
        slider.setRange(minv, maxv)
        slider.setValue(int(self.config.get(key, minv)))

        def on_change(v):
            self.config[key] = v
            value_label.setText(f"{v}{suffix}")
            self._emit_change()

        slider.valueChanged.connect(on_change)
        row.addWidget(slider)
        layout.addLayout(row)
        return slider

    def _checkbox_row(self, layout, label_text, key):
        cb = QCheckBox(label_text)
        cb.setChecked(bool(self.config.get(key, False)))

        def on_change(state):
            self.config[key] = bool(state)
            self._emit_change()

        cb.stateChanged.connect(on_change)
        layout.addWidget(cb)
        return cb

    def _color_button(self, layout, label_text, key):
        row = QHBoxLayout()
        row.addWidget(QLabel(label_text))
        btn = QPushButton()
        btn.setFixedSize(34, 26)
        current = self.config.get(key, "#000000")
        btn.setStyleSheet(f"background-color:{current}; border:1px solid #232A35; border-radius:4px;")

        def pick():
            color = QColorDialog.getColor(QColor(self.config.get(key, "#000000")), self, "Choose color")
            if color.isValid():
                hexval = color.name()
                self.config[key] = hexval
                btn.setStyleSheet(f"background-color:{hexval}; border:1px solid #232A35; border-radius:4px;")
                self._emit_change()

        btn.clicked.connect(pick)
        row.addWidget(btn)
        layout.addLayout(row)
        return btn

    # ---------------- groups ----------------

    def _build_presets_group(self):
        layout = self._add_group("Presets")
        grid = QGridLayout()
        for i, preset in enumerate(presets_mod.BUILTIN_PRESETS):
            btn = QPushButton(preset["name"])
            btn.clicked.connect(lambda checked=False, p=preset: self._apply_preset(p))
            grid.addWidget(btn, i // 2, i % 2)
        layout.addLayout(grid)

        layout.addWidget(QLabel("My Saved Presets:"))
        self.saved_list = QListWidget()
        self.saved_list.setMaximumHeight(120)
        layout.addWidget(self.saved_list)

        row = QHBoxLayout()
        load_btn = QPushButton("Load Selected")
        load_btn.clicked.connect(self._load_selected_preset)
        del_btn = QPushButton("Delete Selected")
        del_btn.setObjectName("danger")
        del_btn.clicked.connect(self._delete_selected_preset)
        row.addWidget(load_btn)
        row.addWidget(del_btn)
        layout.addLayout(row)

        self._refresh_saved_list()

    def _refresh_saved_list(self):
        self.saved_list.clear()
        for name, path in presets_mod.list_user_presets():
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, path)
            self.saved_list.addItem(item)

    def _load_selected_preset(self):
        item = self.saved_list.currentItem()
        if not item:
            return
        path = item.data(Qt.UserRole)
        cfg = presets_mod.load_preset_file(path)
        self._apply_full_config(cfg)

    def _delete_selected_preset(self):
        item = self.saved_list.currentItem()
        if not item:
            return
        path = item.data(Qt.UserRole)
        presets_mod.delete_user_preset(path)
        self._refresh_saved_list()

    def _build_shape_group(self):
        layout = self._add_group("Shape")
        self._checkbox_row(layout, "Cross lines", "crossEnabled")
        self._checkbox_row(layout, "T-Shape (hide top line)", "tShape")
        self._checkbox_row(layout, "Circle outline", "circleEnabled")
        self._checkbox_row(layout, "Center dot", "centerDot")
        self._slider_row(layout, "Rotation", "rotation", 0, 90, "°")

    def _build_color_group(self):
        layout = self._add_group("Color & Opacity")
        swatch_row = QHBoxLayout()
        for c in SWATCHES:
            b = QPushButton()
            b.setFixedSize(24, 24)
            b.setStyleSheet(f"background-color:{c}; border:1px solid #232A35; border-radius:4px;")
            b.clicked.connect(lambda checked=False, col=c: self._set_color(col))
            swatch_row.addWidget(b)
        layout.addLayout(swatch_row)
        self._color_button(layout, "Custom color", "color")
        self._slider_row(layout, "Opacity", "opacity", 10, 100, "%")

    def _set_color(self, color_hex):
        self.config["color"] = color_hex
        self._emit_change()

    def _build_lines_group(self):
        layout = self._add_group("Lines")
        self._slider_row(layout, "Thickness", "thickness", 1, 12, "px")
        self._slider_row(layout, "Length", "length", 2, 40, "px")
        self._slider_row(layout, "Center gap", "gap", 0, 30, "px")

    def _build_dot_group(self):
        layout = self._add_group("Center Dot")
        self._slider_row(layout, "Size", "dotSize", 1, 14, "px")
        self._slider_row(layout, "Opacity", "dotOpacity", 10, 100, "%")

    def _build_circle_group(self):
        layout = self._add_group("Circle")
        self._slider_row(layout, "Radius", "circleRadius", 6, 60, "px")
        self._slider_row(layout, "Thickness", "circleThickness", 1, 8, "px")

    def _build_outline_group(self):
        layout = self._add_group("Outline")
        self._checkbox_row(layout, "Enable outline", "outlineEnabled")
        self._color_button(layout, "Outline color", "outlineColor")
        self._slider_row(layout, "Width", "outlineWidth", 1, 4, "px")
        self._slider_row(layout, "Opacity", "outlineOpacity", 10, 100, "%")

    def _build_save_group(self):
        layout = self._add_group("Save Crosshair")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Name this crosshair")
        layout.addWidget(self.name_input)
        save_btn = QPushButton("Save to My Presets")
        save_btn.setObjectName("primary")
        save_btn.clicked.connect(self._save_current)
        layout.addWidget(save_btn)
        hint = QLabel("Saved presets are written to the presets/ folder next to this app and persist between runs.")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

    def _save_current(self):
        name = self.name_input.text().strip() or "Untitled"
        self.config["name"] = name
        presets_mod.save_user_preset(self.config)
        self.name_input.clear()
        self._refresh_saved_list()

    def _build_import_export_group(self):
        layout = self._add_group("Import / Export")
        import_btn = QPushButton("Import JSON...")
        import_btn.clicked.connect(self._import_json)
        export_btn = QPushButton("Export Current as JSON...")
        export_btn.clicked.connect(self._export_json)
        layout.addWidget(import_btn)
        layout.addWidget(export_btn)

    def _import_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Crosshair", "", "JSON Files (*.json)")
        if not path:
            return
        try:
            cfg = presets_mod.load_preset_file(path)
            self._apply_full_config(cfg)
        except Exception as e:
            QMessageBox.warning(self, "Import failed", f"Could not load that file:\n{e}")

    def _export_json(self):
        import json
        default_name = (self.config.get("name") or "crosshair").replace(" ", "_") + ".json"
        path, _ = QFileDialog.getSaveFileName(self, "Export Crosshair", default_name, "JSON Files (*.json)")
        if not path:
            return
        try:
            with open(path, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Export failed", str(e))

    # ---------------- apply config back to UI ----------------

    def _apply_preset(self, preset):
        cfg = presets_mod.make_config(preset)
        self._apply_full_config(cfg)

    def _apply_full_config(self, cfg):
        self.config = copy.deepcopy(cfg)
        # Rebuild the form so every slider/checkbox reflects the new config.
        self._rebuild_form()
        self._emit_change()

    def _rebuild_form(self):
        # Clear and rebuild the scrollable form area with fresh widgets bound to self.config
        while self.form.count():
            item = self.form.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
        self._build_presets_group()
        self._build_shape_group()
        self._build_color_group()
        self._build_lines_group()
        self._build_dot_group()
        self._build_circle_group()
        self._build_outline_group()
        self._build_save_group()
        self._build_import_export_group()
        self.form.addStretch(1)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def closeEvent(self, event):
        # Pressing the window's X button fully quits the app (overlay + tray
        # included) instead of just hiding the panel to the tray.
        event.accept()
        self.quitRequested.emit()
