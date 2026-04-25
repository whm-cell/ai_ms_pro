param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Target,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$TargetArgs
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

function New-PythonCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Command,

        [string[]]$Args = @()
    )

    [pscustomobject]@{
        Command = $Command
        Args = @($Args)
    }
}

function Get-PythonCandidatesFromPrefix {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Prefix
    )

    if ([string]::IsNullOrWhiteSpace($Prefix) -or -not (Test-Path $Prefix)) {
        return @()
    }

    $candidates = @(
        (Join-Path $Prefix "Scripts\python.exe"),
        (Join-Path $Prefix "Scripts\python"),
        (Join-Path $Prefix "bin\python"),
        (Join-Path $Prefix "bin\python3"),
        (Join-Path $Prefix "python.exe"),
        (Join-Path $Prefix "python")
    )

    $results = @()
    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            $results += (New-PythonCommand -Command $candidate)
        }
    }
    return $results
}

function Get-CommonWindowsPythonCandidates {
    $roots = @()
    if ($env:LOCALAPPDATA) {
        $roots += (Join-Path $env:LOCALAPPDATA "Programs\Python")
    }

    $results = @()
    foreach ($root in $roots) {
        if (-not (Test-Path $root)) {
            continue
        }
        $dirs = Get-ChildItem -Path $root -Directory -Filter "Python*" -ErrorAction SilentlyContinue |
            Sort-Object Name -Descending
        foreach ($dir in $dirs) {
            $candidate = Join-Path $dir.FullName "python.exe"
            if (Test-Path $candidate) {
                $results += (New-PythonCommand -Command $candidate)
            }
        }
    }
    return $results
}

function Test-PythonCommand {
    param(
        [Parameter(Mandatory = $true)]
        $Candidate
    )

    try {
        & $Candidate.Command @($Candidate.Args) -c "import sys" *> $null
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

function Resolve-PythonCommand {
    $candidates = @()

    $candidates += Get-PythonCandidatesFromPrefix -Prefix (Join-Path $Root ".codex\.venv")

    foreach ($envVar in @("VIRTUAL_ENV", "CONDA_PREFIX")) {
        $prefix = [Environment]::GetEnvironmentVariable($envVar)
        if (-not [string]::IsNullOrWhiteSpace($prefix)) {
            $candidates += Get-PythonCandidatesFromPrefix -Prefix $prefix
        }
    }

    if ($env:CODEX_HARNESS_PYTHON) {
        $candidates += (New-PythonCommand -Command $env:CODEX_HARNESS_PYTHON)
    }

    try {
        $python = Get-Command python -ErrorAction Stop
        $candidates += (New-PythonCommand -Command $python.Source)
    } catch {
    }

    try {
        $py = Get-Command py -ErrorAction Stop
        $candidates += (New-PythonCommand -Command $py.Source -Args @("-3"))
    } catch {
    }

    $candidates += Get-CommonWindowsPythonCandidates

    foreach ($candidate in $candidates) {
        if (Test-PythonCommand -Candidate $candidate) {
            return $candidate
        }
    }

    throw "ERROR: could not determine a runnable Python executable for harness scripts"
}

function Resolve-TargetPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RawTarget
    )

    if ([System.IO.Path]::IsPathRooted($RawTarget)) {
        return (Resolve-Path $RawTarget).Path
    }

    $candidate = Join-Path $Root $RawTarget
    if (-not (Test-Path $candidate)) {
        throw "ERROR: target script not found: $RawTarget"
    }
    return (Resolve-Path $candidate).Path
}

$pythonCommand = Resolve-PythonCommand
$targetPath = Resolve-TargetPath -RawTarget $Target

& $pythonCommand.Command @($pythonCommand.Args) $targetPath @TargetArgs
exit $LASTEXITCODE
