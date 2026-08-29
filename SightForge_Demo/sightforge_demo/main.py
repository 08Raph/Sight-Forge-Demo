"""
SightForge Demo — Desktop
----------------------------
A full app for customizing and displaying a crosshair overlay on top of any
windowed or borderless-windowed game.

    python main.py

- A control panel window opens with live sliders/presets (same design as
  the browser version) — every change updates the on-screen overlay
  instantly.
- A system tray icon lets you show/hide the control panel and the overlay,
  or quit.
- F9 toggles the overlay on/off from anywhere (needs the optional
  `keyboard` package).
- Presets you save are written to disk in presets/ and are available next
  time you launch the app.

LIMITATIONS
- Only draws over windowed / borderless-windowed applications. True
  fullscreen-exclusive games bypass the desktop compositor, so nothing will
  be drawn there.
- On Linux + Wayland, always-on-top/click-through is restricted by most
  compositors. X11 and Windows are the reliable targets.
- Some games' anti-cheat prohibits any overlay, even a cosmetic one. Check
  your game's rules first.
"""

import os
import sys

from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QPixmap, QPainter, QPen, QColor, QAction, QDesktopServices
from PySide6.QtCore import Qt, QUrl

import presets as presets_mod
import control_panel
from overlay import CrosshairOverlay
from control_panel import ControlPanel


def _resource_path(relative_path):
    """Resolve a bundled resource whether running from source or from a
    PyInstaller-built exe (where files live under sys._MEIPASS)."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def load_app_icon():
    """Load the SightForge logo for use as the app/taskbar/window icon.
    Prefers the .ico (has multiple sizes baked in, best on Windows) and
    falls back to the .png so it still works on macOS/Linux or from source."""
    ico_path = _resource_path(os.path.join("assets", "icon.ico"))
    png_path = _resource_path(os.path.join("assets", "logo.png"))
    if os.path.exists(ico_path):
        return QIcon(ico_path)
    if os.path.exists(png_path):
        return QIcon(png_path)
    return make_tray_icon()  # last-resort fallback so the app never crashes without assets


def make_tray_icon():
    pix = QPixmap(32, 32)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor("#39ff14"), 2))
    p.drawLine(16, 4, 16, 12)
    p.drawLine(16, 20, 16, 28)
    p.drawLine(4, 16, 12, 16)
    p.drawLine(20, 16, 28, 16)
    p.end()
    return QIcon(pix)


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    app_icon = load_app_icon()
    app.setWindowIcon(app_icon)  # sets the taskbar icon for every window in the app

    screens = QApplication.screens()
    config = presets_mod.load_last_used()

    overlay = CrosshairOverlay(config, screen=screens[0])
    overlay.show()

    panel = ControlPanel(config, screens)
    panel.setWindowIcon(app_icon)
    panel.show()

    # --- wire signals ---
    def on_config_changed(cfg):
        overlay.set_config(cfg)
        presets_mod.save_last_used(cfg)

    panel.configChanged.connect(on_config_changed)

    def toggle_overlay():
        if overlay.isVisible():
            overlay.hide()
            panel.toggle_btn.setText("Show Overlay")
            tray_toggle_action.setText("Show Overlay")
        else:
            overlay.show()
            panel.toggle_btn.setText("Hide Overlay")
            tray_toggle_action.setText("Hide Overlay")

    panel.toggleOverlayRequested.connect(toggle_overlay)

    def change_screen(index):
        if 0 <= index < len(screens):
            overlay.set_screen(screens[index])

    panel.screenChangeRequested.connect(change_screen)
    panel.quitRequested.connect(app.quit)

    # --- tray icon ---
    tray = QSystemTrayIcon(app_icon)
    tray.setToolTip("SightForge Demo")
    menu = QMenu()

    show_panel_action = QAction("Show Control Panel")
    show_panel_action.triggered.connect(lambda: (panel.show(), panel.raise_(), panel.activateWindow()))
    menu.addAction(show_panel_action)

    tray_toggle_action = QAction("Hide Overlay")
    tray_toggle_action.triggered.connect(toggle_overlay)
    menu.addAction(tray_toggle_action)

    menu.addSeparator()
    buy_action = QAction("Get the full version…")
    buy_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(control_panel.BUY_URL)))
    menu.addAction(buy_action)

    discord_action = QAction("Join the Discord")
    discord_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(control_panel.DISCORD_URL)))
    menu.addAction(discord_action)

    menu.addSeparator()
    quit_action = QAction("Quit")
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)

    tray.setContextMenu(menu)
    tray.show()

    # --- optional global hotkey ---
    try:
        import keyboard  # type: ignore
        keyboard.add_hotkey("f9", toggle_overlay)
    except Exception:
        print("Note: install the 'keyboard' package for the F9 toggle hotkey "
              "(pip install keyboard). Tray menu still works without it.")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
