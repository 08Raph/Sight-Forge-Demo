# SightForge Demo — Desktop

A full desktop app for designing and displaying a crosshair overlay on top of
any windowed or borderless-windowed game. One control panel window with live
sliders and presets — no exporting/importing needed, every change shows up on
screen instantly.

## Project files

- `main.py` — entry point, wires everything together, system tray icon
- `control_panel.py` — the settings window (sliders, presets, save/import/export)
- `overlay.py` — the actual fullscreen click-through overlay window
- `render.py` — shared drawing code used by both the preview and the overlay
- `presets.py` — default config, built-in preset library, disk persistence
- `presets/` — your saved presets live here as `.json` files (auto-created)
- `current_crosshair.json` — remembers your last-used crosshair between runs

## Setup

1. Install Python 3.9+ if you don't already have it.
2. In this folder, install dependencies:
   ```
   pip install -r requirements.txt
   ```
   `keyboard` is optional — it only enables the F9 toggle hotkey. Everything
   else works without it.
3. Run it:
   ```
   python main.py
   ```

Two things open: the **control panel** (sliders, presets, color pickers) and
the **overlay** itself, drawn on top of your screen. Adjust anything in the
panel and the overlay updates live.

A small crosshair icon also appears in your system tray. Right-click it for:
- **Show Control Panel** — brings the settings window back if you closed it
- **Hide/Show Overlay**
- **Quit**

Closing the control panel window just hides it (use the tray icon to bring it
back) — only "Quit" from the tray menu or the panel's Quit button fully exits
the app.

Press **F9** anywhere to toggle the overlay on/off (if `keyboard` is installed).

If you have more than one monitor, a **screen selector** appears in the panel
so you can choose which display the overlay is drawn on.

## Presets

Click any built-in preset to load it. To keep your own tweaks: type a name
under **Save Crosshair** and click **Save to My Presets** — it's written to
`presets/<name>.json` and shows up in "My Saved Presets" every time you
relaunch the app. You can also **Export** the current crosshair to any
location as a standalone `.json` file (to share with a friend, for instance)
and **Import** one back in.

## Notes and limitations

- **Windowed / borderless-windowed games only.** True fullscreen-exclusive
  mode bypasses the desktop compositor entirely, so nothing will be drawn
  there. Most modern games default to borderless windowed, which works fine.
- **Linux + Wayland**: click-through and always-on-top are restricted by
  design in most Wayland compositors. X11 and Windows are the reliable
  targets; if you're on Wayland, try running under XWayland or switch to an
  X11 session.
- **Anti-cheat**: some competitive games (e.g. titles using Vanguard-style
  kernel anti-cheat) prohibit any third-party overlay, even a purely
  cosmetic one, and can flag or ban for running one. Check your game's
  rules first.
- On Windows, if click-through doesn't fully work in a specific game, that
  game is likely intercepting input at a lower level than Qt's
  `WindowTransparentForInput` flag reaches — there's no safe workaround for
  that within this app's design.

## Packaging as a standalone executable (optional)

If you want a double-clickable app instead of running `python main.py`:

```
pip install pyinstaller
pyinstaller --onefile --noconsole --name CrosshairOverlay main.py
```

The executable will be in the `dist/` folder. Note it will still need to be
distributed alongside its dependencies being bundled correctly — test the
built executable before relying on it.

## Config format

`current_crosshair.json` (auto-created next to `main.py`) stores the active
crosshair and uses the same schema as SightForge Demo's export:

```json
{
  "name": "My Crosshair",
  "color": "#39ff14",
  "opacity": 100,
  "crossEnabled": true,
  "thickness": 2,
  "length": 10,
  "gap": 3,
  "tShape": false,
  "rotation": 0,
  "centerDot": false,
  "dotSize": 2,
  "dotOpacity": 100,
  "circleEnabled": false,
  "circleRadius": 20,
  "circleThickness": 1,
  "outlineEnabled": true,
  "outlineColor": "#000000",
  "outlineWidth": 1,
  "outlineOpacity": 100
}
```

You can hand-edit this file too, or just re-import a new export from
SightForge Demo via the tray menu.
