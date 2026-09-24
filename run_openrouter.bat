@echo off
setlocal

where node >nul 2>&1
if errorlevel 1 (
    echo Node.js is required but was not found on PATH.
    echo Install Node.js 18.17 or newer, then run this file again.
    pause
    exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
    echo npm is required but was not found on PATH. Reinstall Node.js with npm enabled.
    pause
    exit /b 1
)

for /f "delims=" %%P in ('npm prefix -g 2^>nul') do set "NPM_PREFIX=%%P"
if not defined NPM_PREFIX (
    echo Could not determine npm's global install folder.
    pause
    exit /b 1
)
set "PATH=%NPM_PREFIX%;%PATH%"

if not exist "%NPM_PREFIX%\openrouter.cmd" (
    echo Installing OpenRouter CLI...
    call npm install --global @letuscode/openrouter-cli
    if errorlevel 1 (
        echo OpenRouter CLI installation failed.
        pause
        exit /b 1
    )
)

echo Launching OpenRouter CLI. On first run, enter your API key in this window.
pushd "%~dp0"
call "%NPM_PREFIX%\openrouter.cmd"
set "CLI_EXIT=%ERRORLEVEL%"
popd

echo OpenRouter CLI exited with code %CLI_EXIT%.
pause
exit /b %CLI_EXIT%
