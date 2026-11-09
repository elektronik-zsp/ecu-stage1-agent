@echo off
setlocal
pyinstaller --noconfirm --clean --windowed --name ECU_Stage1_Agent main.py
if errorlevel 1 exit /b 1
echo Build completed. Verify the application on Windows before distribution.
