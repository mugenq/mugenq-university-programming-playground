@echo off
setlocal
cd /d "%~dp0"

REM Requires Python 3 on Windows. PyInstaller must run on Windows to build a Windows .exe.
where py >nul 2>nul
if not errorlevel 1 (
    set "PYTHON=py -3"
) else (
    where python >nul 2>nul
    if errorlevel 1 (
        echo Python was not found. Install it from https://www.python.org/downloads/windows/
        pause
        exit /b 1
    )
    set "PYTHON=python"
)

%PYTHON% -m pip install --upgrade pyinstaller
if errorlevel 1 goto :failed
%PYTHON% -m PyInstaller --noconfirm --clean --onefile --windowed --name RedeemWheel --icon "assets\redeem_wheel.ico" --add-data "assets\redeem_wheel.png;assets" --add-data "assets\redeem_wheel.ico;assets" redeem_wheel.py
if errorlevel 1 goto :failed

echo.
echo BUILD COMPLETE: %CD%\dist\RedeemWheel.exe
echo Please scan this exact EXE before sharing. The previous build was flagged by 8/70 vendors including Microsoft.
pause
exit /b 0

:failed
echo.
echo Windows executable build failed. See the error above.
pause
exit /b 1
