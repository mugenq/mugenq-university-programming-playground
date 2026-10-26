@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py -3 redeem_wheel.py
) else (
    python redeem_wheel.py
)
if errorlevel 1 pause
