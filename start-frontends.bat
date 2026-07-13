@echo off
setlocal

set "ROOT=%~dp0"

powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\start-frontends.ps1"

if errorlevel 1 (
    echo.
    echo 前端启动脚本执行失败。
    pause
)

endlocal