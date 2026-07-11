$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot

function Start-Frontend {
    param(
        [Parameter(Mandatory = $true)] [string] $Name,
        [Parameter(Mandatory = $true)] [string] $RelativePath,
        [Parameter(Mandatory = $true)] [int] $Port
    )

    $projectPath = Join-Path $root $RelativePath
    if (-not (Test-Path $projectPath)) {
        throw "Project path not found: $projectPath"
    }

    $command = @"
`$Host.UI.RawUI.WindowTitle = '$Name'
Set-Location '$projectPath'
if (-not (Test-Path 'node_modules')) {
  Write-Host 'Installing dependencies for $Name...' -ForegroundColor Cyan
  npm install
  if (`$LASTEXITCODE -ne 0) { exit `$LASTEXITCODE }
}
Write-Host 'Starting $Name at http://127.0.0.1:$Port' -ForegroundColor Green
npm run dev -- --host 127.0.0.1 --port $Port --strictPort
"@

    Start-Process powershell -ArgumentList @(
        '-NoExit',
        '-NoProfile',
        '-ExecutionPolicy', 'Bypass',
        '-Command', $command
    ) -WorkingDirectory $projectPath
}

Start-Frontend -Name 'teacher-web' -RelativePath 'frontend\teacher-web' -Port 5173
Start-Frontend -Name 'student-web' -RelativePath 'frontend\student-web' -Port 5174

Write-Host '已打开两个前端启动窗口：' -ForegroundColor Green
Write-Host '教师端：http://127.0.0.1:5173'
Write-Host '学生端：http://127.0.0.1:5174'
Write-Host '关闭对应 PowerShell 窗口即可停止服务。'
