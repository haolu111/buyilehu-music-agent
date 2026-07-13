$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$pythonRoot = Join-Path $root "backend\python-capability-library"
$javaRoot = Join-Path $root "backend\music-agent-server"
$venvPython = Join-Path $pythonRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    throw "Python capability environment is missing. Use Python 3.11+: cd backend\python-capability-library; py -3.11 -m venv .venv; .\.venv\Scripts\pip install -r requirements.txt"
}

$version = & $venvPython -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ([version]$version -lt [version]"3.11") {
    throw "Python 3.11+ is required; capability environment currently uses Python $version."
}

Start-Process -FilePath $venvPython -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8001" -WorkingDirectory $pythonRoot -WindowStyle Hidden

$ready = $false
for ($attempt = 0; $attempt -lt 30; $attempt++) {
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/v1/health" -TimeoutSec 1
        if ($health.success) { $ready = $true; break }
    } catch {}
    Start-Sleep -Milliseconds 500
}
if (-not $ready) { throw "Python capability service did not become healthy on port 8001." }

$env:PYTHON_CAPABILITY_ENABLED = "true"
$env:PYTHON_CAPABILITY_CALL_MODE = "primary"
$env:PYTHON_CAPABILITY_BASE_URL = "http://127.0.0.1:8001"
Set-Location $javaRoot
mvn spring-boot:run
