@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo No existe el entorno virtual .venv
    echo.
    echo Ejecuta primero estos comandos:
    echo python -m venv .venv
    echo .\.venv\Scripts\python.exe -m pip install --upgrade pip
    echo .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo Iniciando servidor local en http://127.0.0.1:3001
echo.
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 3001

pause
