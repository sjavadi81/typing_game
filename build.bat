@echo off
echo ============================================
echo Building Typing App .EXE
echo ============================================

REM Build the executable
pyinstaller --onefile --windowed typing_app.py

echo.
echo Build complete!
echo Your EXE is located in the "dist" folder.
pause
