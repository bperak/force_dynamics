$ErrorActionPreference = "Stop"

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "Run this script as Administrator."
    exit 1
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$systemPython = "C:\Python313\python.exe"
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"

New-NetFirewallRule -DisplayName "Python OpenAI Outbound" -Direction Outbound -Program $systemPython -Action Allow | Out-Null
New-NetFirewallRule -DisplayName "Venv Python OpenAI Outbound" -Direction Outbound -Program $venvPython -Action Allow | Out-Null

Test-NetConnection api.openai.com -Port 443
