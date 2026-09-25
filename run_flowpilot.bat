@echo off
setlocal
set "ROOT=%~dp0"
cd /d "%ROOT%"

where python >nul 2>&1
if errorlevel 1 (
    echo Python was not found on PATH. Install Python 3.10 or newer, then retry.
    pause
    exit /b 1
)
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 (
    echo FlowPilot requires Python 3.10 or newer.
    pause
    exit /b 1
)

where node >nul 2>&1
if errorlevel 1 (
    echo Node.js was not found on PATH. Install Node.js 20.9 or newer, then retry.
    pause
    exit /b 1
)
node -e "const v=process.versions.node.split('.').map(Number); process.exit(v[0]>20||(v[0]===20&&v[1]>=9)?0:1)" >nul 2>&1
if errorlevel 1 (
    echo FlowPilot's Next.js frontend requires Node.js 20.9 or newer.
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
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
"%PYTHON%" -m pip install --disable-pip-version-check -r "%ROOT%requirements.txt"
if errorlevel 1 goto :setup_failed

if not exist "%ROOT%node_modules\next\package.json" (
    echo Installing frontend dependencies...
    pushd "%ROOT%"
    call npm.cmd install
    set "NPM_EXIT=%ERRORLEVEL%"
    popd
    if not "%NPM_EXIT%"=="0" goto :setup_failed
)

if not exist "%ROOT%.env" (
    if exist "%ROOT%.env.example" copy /y "%ROOT%.env.example" "%ROOT%.env" >nul
    echo Created .env from the example if available. Configure PostgreSQL and an AI provider key, then run this launcher again.
    pause
    exit /b 1
)

echo Validating required configuration...
"%PYTHON%" -c "from dotenv import load_dotenv; import os,sys; load_dotenv('.env'); u=os.getenv('DATABASE_URL','').strip().lower(); ai=any(os.getenv(k,'').strip() for k in ('GEMINI_API_KEY','OPENAI_API_KEY')); sys.exit(0 if u.startswith(('postgresql://','postgresql+','postgres://')) and ai else 1)" >nul 2>&1
if errorlevel 1 (
    echo .env must contain a PostgreSQL DATABASE_URL and at least one AI provider key.
    echo Values are not displayed. Edit .env and run this launcher again.
    pause
    exit /b 1
)

echo Checking PostgreSQL connection...
"%PYTHON%" "%ROOT%scripts\check_postgres.py"
if errorlevel 1 (
    echo PostgreSQL is not reachable. Check DATABASE_URL and start its database service.
    pause
    exit /b 1
)

echo Applying Alembic migrations...
"%PYTHON%" -m alembic -c "%ROOT%backend\alembic.ini" upgrade head
if errorlevel 1 goto :setup_failed

echo Starting FlowPilot backend and frontend in separate terminals...
curl.exe --silent --output nul --fail --max-time 2 http://localhost:8000/docs >nul 2>&1
if errorlevel 1 start "FlowPilot Backend" powershell.exe -NoExit -ExecutionPolicy Bypass -Command "Set-Location -LiteralPath '%ROOT%'; & '%PYTHON%' -m uvicorn backend.main:app --reload --port 8000"
curl.exe --silent --output nul --fail --max-time 2 http://localhost:3000 >nul 2>&1
if errorlevel 1 start "FlowPilot Frontend" powershell.exe -NoExit -ExecutionPolicy Bypass -Command "Set-Location -LiteralPath '%ROOT%'; npm.cmd run dev"

echo Waiting for FlowPilot servers...
set "ATTEMPT=0"
:wait_for_servers
set /a ATTEMPT+=1
if not defined BACKEND_READY (
    curl.exe --silent --output nul --fail --max-time 2 http://localhost:8000/docs >nul 2>&1
    if not errorlevel 1 set "BACKEND_READY=1"
)
if not defined FRONTEND_READY (
    curl.exe --silent --output nul --fail --max-time 2 http://localhost:3000 >nul 2>&1
    if not errorlevel 1 set "FRONTEND_READY=1"
)
if defined BACKEND_READY if defined FRONTEND_READY goto :open_apps
if %ATTEMPT% GEQ 30 goto :server_timeout
timeout /t 2 /nobreak >nul
goto :wait_for_servers

:open_apps
start "" "http://localhost:3000"
start "" "http://localhost:8000/docs"
echo FlowPilot frontend and backend are ready.
exit /b 0

:server_timeout
if defined FRONTEND_READY start "" "http://localhost:3000"
if defined BACKEND_READY start "" "http://localhost:8000/docs"
if not defined FRONTEND_READY echo Frontend did not respond. Check the FlowPilot Frontend terminal.
if not defined BACKEND_READY echo Backend did not respond. Check the FlowPilot Backend terminal.
pause
exit /b 1

:setup_failed
echo Setup failed. Review the error above, fix it, then run this launcher again.
pause
exit /b 1
