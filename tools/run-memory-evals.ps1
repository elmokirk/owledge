[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "agent_memory_cli.py"
$python = if ($env:AGENT_MEMORY_PYTHON) { $env:AGENT_MEMORY_PYTHON } else { "python" }
& $python $scriptPath --project-root $ProjectRoot run-evals
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
