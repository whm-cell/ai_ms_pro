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

    return ($null -ne (Get-PythonVersionScore -Candidate $Candidate))
}

function Get-PythonVersionScore {
    param(
        [Parameter(Mandatory = $true)]
        $Candidate
    )

    try {
        $output = & $Candidate.Command @($Candidate.Args) -c "import sys; v=sys.version_info; print(v[0] * 1000000 + v[1] * 1000 + v[2])" 2> $null
        if ($LASTEXITCODE -ne 0) {
            return $null
        }
        $rendered = ($output | Select-Object -First 1).ToString().Trim()
        if ($rendered -match '^\d+$') {
            return [int]$rendered
        }
        return $null
    } catch {
        return $null
    }
}

function Select-BestPythonCommand {
    param(
        [Parameter(Mandatory = $true)]
        [object[]]$Candidates
    )

    $preferredMinScore = 3 * 1000000 + 11 * 1000
    $best = $null
    $bestScore = -1
    $bestIsPreferred = $false

    foreach ($candidate in $Candidates) {
        $score = Get-PythonVersionScore -Candidate $candidate
        if ($null -eq $score) {
            continue
        }

        $isPreferred = ($score -ge $preferredMinScore)
        if (($isPreferred -and -not $bestIsPreferred) -or (($isPreferred -eq $bestIsPreferred) -and ($score -gt $bestScore))) {
            $best = $candidate
            $bestScore = $score
            $bestIsPreferred = $isPreferred
        }
    }

    return $best
}

function Resolve-PythonCommand {
    $prefixCandidates = @()

    $prefixCandidates += Get-PythonCandidatesFromPrefix -Prefix (Join-Path $Root ".codex\.venv")

    foreach ($envVar in @("VIRTUAL_ENV", "CONDA_PREFIX")) {
        $prefix = [Environment]::GetEnvironmentVariable($envVar)
        if (-not [string]::IsNullOrWhiteSpace($prefix)) {
            $prefixCandidates += Get-PythonCandidatesFromPrefix -Prefix $prefix
        }
    }

    foreach ($candidate in $prefixCandidates) {
        if (Test-PythonCommand -Candidate $candidate) {
            return $candidate
        }
    }

    if ($env:CODEX_HARNESS_PYTHON) {
        $explicit = New-PythonCommand -Command $env:CODEX_HARNESS_PYTHON
        if (Test-PythonCommand -Candidate $explicit) {
            return $explicit
        }
    }

    $fallbackCandidates = @()

    foreach ($name in @("python3", "python")) {
        try {
            $python = Get-Command $name -ErrorAction Stop
            $fallbackCandidates += (New-PythonCommand -Command $python.Source)
        } catch {
        }
    }

    try {
        $py = Get-Command py -ErrorAction Stop
        $fallbackCandidates += (New-PythonCommand -Command $py.Source -Args @("-3"))
    } catch {
    }

    $fallbackCandidates += Get-CommonWindowsPythonCandidates

    $bestFallback = Select-BestPythonCommand -Candidates $fallbackCandidates
    if ($null -ne $bestFallback) {
        return $bestFallback
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
