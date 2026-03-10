@echo off
setlocal

set SCRIPT_DIR=%~dp0

where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py "%SCRIPT_DIR%scripts\start_backend.py" %*
) else (
  python "%SCRIPT_DIR%scripts\start_backend.py" %*
)
