@echo off
REM ============================================================
REM  Build AFKing.exe  --  run this once, get dist\AFKing.exe
REM  Requires: Python 3 installed and on PATH.
REM ============================================================

echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller
if errorlevel 1 goto :error

echo Generating icon...
python make_icon.py
if errorlevel 1 goto :error

echo Building AFKing.exe...
pyinstaller --noconfirm --onefile --windowed ^
    --name AFKing ^
    --icon afking.ico ^
    --version-file version.txt ^
    --noupx ^
    --hidden-import pystray._win32 ^
    afking.py
if errorlevel 1 goto :error

echo.
echo ============================================================
echo  Done!  Your app is here:  dist\AFKing.exe
echo  You can copy that single file anywhere and double-click it.
echo ============================================================
goto :end

:error
echo.
echo Build failed. Scroll up to see what went wrong.

:end
pause
