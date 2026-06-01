[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-AgentMemoryCli {
  $local = Join-Path $PSScriptRoot "agent_memory_cli.py"
  if (Test-Path -LiteralPath $local) { return $local }
  $repo = Join-Path $PSScriptRoot "..\..\..\tools\agent_memory_cli.py"
  if (Test-Path -LiteralPath $repo) { return (Resolve-Path -LiteralPath $repo).Path }
  $projectCli = Join-Path $ProjectRoot "tools\agent_memory_cli.py"
  if (Test-Path -LiteralPath $projectCli) { return (Resolve-Path -LiteralPath $projectCli).Path }
  throw "Cannot find agent_memory_cli.py. Install the Agent Memory Kit tools first."
}

$python = if ($env:AGENT_MEMORY_PYTHON) { $env:AGENT_MEMORY_PYTHON } else { "python" }
& $python (Resolve-AgentMemoryCli) --project-root $ProjectRoot compliance-doctor
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
