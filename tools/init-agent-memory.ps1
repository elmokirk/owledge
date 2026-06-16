[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path,
  [string]$KitRoot = "",
  [switch]$Force,
  [switch]$IncludeCompliance,
  [switch]$RuntimeOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Test-KitRoot {
  param([string]$Path)
  if ([string]::IsNullOrWhiteSpace($Path)) { return $false }
  return (
    (Test-Path -LiteralPath (Join-Path $Path "PROJECT_CONTEXT.template.md")) -and
    (Test-Path -LiteralPath (Join-Path $Path "tools\bootstrap-agent-memory.ps1")) -and
    (Test-Path -LiteralPath (Join-Path $Path "tools\agent_memory_cli.py"))
  )
}

$localKitRoot = Split-Path -Parent $PSScriptRoot
$python = if ($env:AGENT_MEMORY_PYTHON) { $env:AGENT_MEMORY_PYTHON } else { "python" }
$effectiveKitRoot = $null
if (Test-KitRoot -Path $KitRoot) {
  $effectiveKitRoot = (Resolve-Path -LiteralPath $KitRoot).Path
} elseif (Test-KitRoot -Path $localKitRoot) {
  $effectiveKitRoot = (Resolve-Path -LiteralPath $localKitRoot).Path
}

if (-not $RuntimeOnly -and $effectiveKitRoot) {
  $bootstrap = Join-Path $effectiveKitRoot "tools\bootstrap-agent-memory.ps1"
  $bootstrapArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $bootstrap, "-ProjectRoot", $ProjectRoot, "-KitRoot", $effectiveKitRoot)
  if ($Force) { $bootstrapArgs += "-Force" }
  if ($IncludeCompliance) { $bootstrapArgs += "-IncludeCompliance" }
  powershell @bootstrapArgs
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  exit 0
}

$scriptPath = Join-Path $PSScriptRoot "agent_memory_cli.py"
& $python $scriptPath --project-root $ProjectRoot init
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $python $scriptPath --project-root $ProjectRoot doctor --mode host
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
