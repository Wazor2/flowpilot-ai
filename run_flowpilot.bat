@echo off
setlocal
set "ROOT=%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo Python was not found on PATH. Install Python 3.11 or newer, then retry.
    pause
    exit /b 1
)

where node >nul 2>&1
if errorlevel 1 (
    echo Node.js was not found on PATH. Install Node.js 18.17 or newer, then retry.
    pause
    exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
    echo npm was not found on PATH. Reinstall Node.js with npm enabled, then retry.
    pause
    exit /b 1
)

if not exist "%ROOT%.venv\Scripts\python.exe" (
    echo Creating the Python virtual environment...
    python -m venv "%ROOT%.venv"
    if errorlevel 1 goto :setup_failed
)

echo Checking backend dependencies...
"%ROOT%.venv\Scripts\python.exe" -m pip install -r "%ROOT%requirements.txt"
if errorlevel 1 goto :setup_failed

if not exist "%ROOT%node_modules\next\package.json" (
    echo Installing frontend dependencies...
    pushd "%ROOT%"
    call npm.cmd install
    set "NPM_EXIT=%ERRORLEVEL%"
    popd
    if not "%NPM_EXIT%"=="0" goto :setup_failed
)

echo Starting FlowPilot backend and frontend in separate terminals...
start "FlowPilot Backend" powershell.exe -NoExit -ExecutionPolicy Bypass -Command "Set-Location -LiteralPath '%ROOT%'; & '%ROOT%.venv\Scripts\python.exe' -m uvicorn backend.main:app --reload --port 8000"
start "FlowPilot Frontend" powershell.exe -NoExit -ExecutionPolicy Bypass -Command "Set-Location -LiteralPath '%ROOT%'; npm.cmd run dev"
exit /b 0

:setup_failed
echo Setup failed. Review the error above, fix it, then run this launcher again.
pause
exit /b 1
