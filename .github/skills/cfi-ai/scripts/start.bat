@echo off
setlocal
cd /d "%~dp0"

echo === Bootstrapping samples\Python environment ===

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv || goto :error
) else (
    echo Virtual environment already exists.
)

call ".venv\Scripts\activate.bat" || goto :error

echo Installing requirements...
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt || goto :error

if not exist ".env" (
    echo Copying .env.example to .env (edit to point at your proxy + key)
    copy /Y ".env.example" ".env" >nul
)

echo.
echo === Running all samples (output also logged to test-results.log) ===
python run_all.py
set RC=%ERRORLEVEL%

echo.
echo Done. See test-results.log for full output.
exit /b %RC%

:error
echo BUILD FAILED
exit /b 1
