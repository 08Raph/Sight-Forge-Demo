@echo off
REM Builds "SightForge Demo.exe" from source. Run this ON WINDOWS, from
REM inside this folder (the same folder as main.py).
REM
REM Requirements: Python 3.9+ installed and on PATH.

echo Installing/upgrading dependencies...
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
py -m pip install --upgrade pyinstaller

echo Building SightForge Demo.exe (this can take a minute or two)...
py -m PyInstaller SightForge_Demo.spec --noconfirm

echo.
echo Done. Your exe is at: dist\SightForge Demo.exe
pause
