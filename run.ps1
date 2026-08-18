param(
    [Parameter(Position = 0)]
    [string]$CommandName = "doctor",
    [Parameter(Position = 1, ValueFromRemainingArguments = $true)]
    [object[]]$CommandArgs
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$CommandArgs = [string[]]@($CommandArgs)

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw "Missing .venv. Run .\bootstrap.ps1 first."
}

$scriptPath = $null
$forward = @()
$name = $CommandName.ToLowerInvariant()

switch ($name) {
    "doctor" {
        $scriptPath = Join-Path $RepoRoot "scripts\doctor.py"
        $forward = if ($CommandArgs.Count -eq 0) { @("--scan-timeout", "5") } else { [string[]]@($CommandArgs) }
    }
    "scan" {
        $scriptPath = Join-Path $RepoRoot "scripts\scan.py"
        $forward = if ($CommandArgs.Count -eq 0) { @("--timeout", "15", "--name", "FRG") } else { [string[]]@($CommandArgs) }
    }
    "inspect" {
        $scriptPath = Join-Path $RepoRoot "scripts\inspect.py"
        $forward = if ($CommandArgs.Count -eq 0) { @("--device", "FRG") } else { [string[]]@($CommandArgs) }
    }
    "read" { 
        $scriptPath = Join-Path $RepoRoot "scripts\read_safe.py"
        $forward = if ($CommandArgs.Count -eq 0) { @("--device", "FRG") } else { [string[]]@($CommandArgs) }
    }
    "read_safe" {
        $scriptPath = Join-Path $RepoRoot "scripts\read_safe.py"
        $forward = if ($CommandArgs.Count -eq 0) { @("--device", "FRG") } else { [string[]]@($CommandArgs) }
    }
    "monitor" {
        $scriptPath = Join-Path $RepoRoot "scripts\monitor.py"
        if ($CommandArgs.Count -gt 0 -and -not $CommandArgs[0].StartsWith("-")) {
            $label = $CommandArgs[0]
            $duration = if ($CommandArgs.Count -gt 1) { $CommandArgs[1] } else { $null }
            $forward = @("--device", "FRG", "--label", $label, "--all")
            if ($null -ne $duration) { $forward += @("--duration", $duration) }
            if ($CommandArgs.Count -gt 2) { $forward += $CommandArgs[2..($CommandArgs.Count - 1)] }
        } else {
            $forward = [string[]]@($CommandArgs)
        }
    }
    default { throw "Unknown command '$CommandName'. Use doctor, scan, inspect, read or monitor." }
}

if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
    throw "Script not found: $scriptPath"
}

$invoke = @($scriptPath) + @($forward)
& $Python @invoke
exit $LASTEXITCODE
