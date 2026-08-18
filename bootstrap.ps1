param(
    [switch]$InstallPython,
    [switch]$ForceRecreate
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPath = Join-Path $RepoRoot ".venv"
$VenvPython = Join-Path $VenvPath "Scripts\python.exe"
$Requirements = Join-Path $RepoRoot "requirements.txt"
$ConfigExample = Join-Path $RepoRoot "config.example.json"
$Config = Join-Path $RepoRoot "config.json"

function Invoke-Step {
    param([string]$Executable, [string[]]$Arguments)
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed ($LASTEXITCODE): $Executable $($Arguments -join ' ')"
    }
}

function Test-Venv {
    if (-not (Test-Path -LiteralPath $VenvPython -PathType Leaf)) { return $false }
    & $VenvPython -c "import sys; import bleak; print(sys.version); print(bleak.__file__)" 2>$null | Out-Null
    return ($LASTEXITCODE -eq 0)
}

if ((Test-Path -LiteralPath $VenvPath) -and $ForceRecreate) {
    $resolvedVenv = (Resolve-Path -LiteralPath $VenvPath).Path
    $resolvedRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
    if (-not $resolvedVenv.StartsWith($resolvedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to move an unexpected .venv path: $resolvedVenv"
    }
    $backup = Join-Path $RepoRoot (".venv.backup_" + (Get-Date -Format "yyyyMMdd_HHmmss"))
    Move-Item -LiteralPath $VenvPath -Destination $backup
    Write-Host "Existing .venv moved to $backup"
}

if (-not (Test-Venv)) {
    if (Test-Path -LiteralPath $VenvPath) {
        $resolvedVenv = (Resolve-Path -LiteralPath $VenvPath).Path
        $resolvedRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
        if (-not $resolvedVenv.StartsWith($resolvedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to move an unexpected .venv path: $resolvedVenv"
        }
        $backup = Join-Path $RepoRoot (".venv.broken_" + (Get-Date -Format "yyyyMMdd_HHmmss"))
        Move-Item -LiteralPath $VenvPath -Destination $backup
        Write-Host "Broken .venv moved to $backup"
    }

    $selected = $false
    $py = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($null -ne $py) {
        foreach ($minor in @("3.12", "3.13")) {
            & $py.Source ("-" + $minor) -c "import sys; print(sys.executable)" 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "Creating .venv with Python $minor"
                Invoke-Step $py.Source @(("-" + $minor), "-m", "venv", $VenvPath)
                $selected = $true
                break
            }
        }
    }

    if (-not $selected) {
        $python = Get-Command python.exe -ErrorAction SilentlyContinue
        if ($null -eq $python) {
            if ($InstallPython) {
                Write-Host "Installing Python 3.12 with winget..."
                Invoke-Step "winget.exe" @("install", "Python.Python.3.12", "--accept-source-agreements", "--accept-package-agreements")
                $python = Get-Command python.exe -ErrorAction SilentlyContinue
            }
        }
        if ($null -eq $python) {
            throw "No Python launcher found. Install Python 3.12/3.13, then rerun bootstrap.ps1."
        }
        Write-Warning "Python 3.12/3.13 was not found; using the available Python interpreter."
        Invoke-Step $python.Source @("-m", "venv", $VenvPath)
    }
}

if (-not (Test-Path -LiteralPath $VenvPython -PathType Leaf)) {
    throw "The virtual environment was not created: $VenvPython"
}

Write-Host "Using $VenvPython"
Invoke-Step $VenvPython @("-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel")
Invoke-Step $VenvPython @("-m", "pip", "install", "-r", $Requirements)

if ((Test-Path -LiteralPath $ConfigExample) -and -not (Test-Path -LiteralPath $Config)) {
    Copy-Item -LiteralPath $ConfigExample -Destination $Config
    Write-Host "Created local config.json from config.example.json"
}

Invoke-Step $VenvPython @("-m", "pip", "check")
Invoke-Step $VenvPython @( (Join-Path $RepoRoot "scripts\doctor.py"), "--no-scan" )
Write-Host "Bootstrap completed. Use .\run.ps1 doctor or .\.venv\Scripts\python.exe directly."
