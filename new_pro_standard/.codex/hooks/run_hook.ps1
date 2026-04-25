param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$HookScript,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$HookArgs
)

$ErrorActionPreference = "Stop"

if ([System.IO.Path]::IsPathRooted($HookScript)) {
    $target = $HookScript
} elseif ($HookScript -match "[/\\]") {
    $target = $HookScript
} else {
    $target = ".codex/hooks/$HookScript"
}

& (Join-Path $PSScriptRoot "run_with_repo_python.ps1") $target @HookArgs
exit $LASTEXITCODE
