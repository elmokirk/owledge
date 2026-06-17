[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path,
  [switch]$Strict
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "agent_memory_cli.py"
$python = if ($env:AGENT_MEMORY_PYTHON) { $env:AGENT_MEMORY_PYTHON } else { "python" }
$argsList = @($scriptPath, "--project-root", $ProjectRoot, "validate-memory")
if ($Strict) { $argsList += "--strict" }
& $python @argsList
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
