:; exec "$(dirname "$0")/run_hook.sh" "$@"
@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_hook.ps1" %*
exit /b %ERRORLEVEL%
