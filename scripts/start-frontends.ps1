$ErrorActionPreference = "Stop"

# 当前脚本位于 scripts 目录，因此上一级目录是项目根目录
$Root = Split-Path -Parent $PSScriptRoot

$TeacherWeb = Join-Path $Root "frontend\teacher-web"
$StudentWeb = Join-Path $Root "frontend\student-web"

function Start-Frontend {
    param (
        [string]$Name,
        [string]$Path,
        [int]$Port
    )

    if (-not (Test-Path $Path)) {
        Write-Host "未找到 $Name 目录：$Path" -ForegroundColor Red
        return
    }

    # 第一次启动或 node_modules 不存在时才执行 npm install
    $NodeModules = Join-Path $Path "node_modules"

    if (-not (Test-Path $NodeModules)) {
        Write-Host "$Name 尚未安装依赖，正在执行 npm install..." -ForegroundColor Yellow

        Push-Location $Path
        try {
            npm install

            if ($LASTEXITCODE -ne 0) {
                throw "$Name 依赖安装失败"
            }
        }
        finally {
            Pop-Location
        }
    }

    Write-Host "正在启动 $Name，端口：$Port" -ForegroundColor Green

    # 为每个前端打开一个独立 CMD 窗口
    Start-Process cmd.exe -ArgumentList @(
        "/k",
        "title $Name && cd /d `"$Path`" && npm run dev -- --host 127.0.0.1 --port $Port --strictPort"
    )
}

Start-Frontend `
    -Name "Teacher Web" `
    -Path $TeacherWeb `
    -Port 5173

Start-Frontend `
    -Name "Student Web" `
    -Path $StudentWeb `
    -Port 5174

Write-Host ""
Write-Host "前端启动命令已执行：" -ForegroundColor Cyan
Write-Host "教师端：http://127.0.0.1:5173/"
Write-Host "学生端：http://127.0.0.1:5174/"