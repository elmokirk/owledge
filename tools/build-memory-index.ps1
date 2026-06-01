[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path,
  [switch]$Incremental,
  [switch]$TrackTombstones
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "agent_memory_cli.py"
$python = if ($env:AGENT_MEMORY_PYTHON) { $env:AGENT_MEMORY_PYTHON } else { "python" }
$arguments = @($scriptPath, "--project-root", $ProjectRoot, "build-memory-index")
if ($Incremental) { $arguments += "--incremental" }
if ($TrackTombstones) { $arguments += "--track-tombstones" }
& $python @arguments
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
