[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path,
  [string]$HostName = "127.0.0.1",
  [int]$Port = 8765
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "agent_memory_cli.py"
$python = if ($env:AGENT_MEMORY_PYTHON) { $env:AGENT_MEMORY_PYTHON } else { "python" }
& $python $scriptPath --project-root $ProjectRoot serve --host $HostName --port $Port
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
