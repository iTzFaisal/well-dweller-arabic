@echo off
chcp 65001 >nul
setlocal
rem Well Dweller Arabic translation installer.
rem Drag the base game NSP and the v1.0.3 update NSP onto this file,
rem or put them in this folder and double-click it.

where uv >nul 2>nul
if errorlevel 1 (
  echo "uv" is required to run the installer but was not found.
  echo Install it from https://docs.astral.sh/uv/getting-started/installation/
  echo then run this file again.
  pause
  exit /b 1
)

uv run --quiet "%~dp0install.py" %*
pause
