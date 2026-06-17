[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)]
  [string]$KnowledgebaseRoot,
  [string]$KitRoot = "",
  [ValidateSet("module-dir", "flat")]
  [string]$Layout = "module-dir",
  [string]$ModuleDir = "agent-memory-module",
  [string]$MapFile = "",
  [int]$MaxFiles = 10000,
  [switch]$IncludeCli,
  [switch]$NoSamplePlan
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if (Test-Path -LiteralPath Variable:\PSNativeCommandUseErrorActionPreference) {
  $PSNativeCommandUseErrorActionPreference = $false
}

$scriptPath = Join-Path $PSScriptRoot "build_kb_module.py"
$python = if ($env:AGENT_MEMORY_PYTHON) { $env:AGENT_MEMORY_PYTHON } else { "python" }

$argsList = @(
  $scriptPath,
  "--knowledgebase-root", $KnowledgebaseRoot,
  "--layout", $Layout,
  "--module-dir", $ModuleDir,
  "--max-files", [string]$MaxFiles
)
if ($KitRoot) { $argsList += @("--kit-root", $KitRoot) }
if ($MapFile) { $argsList += @("--map-file", $MapFile) }
if ($IncludeCli) { $argsList += "--include-cli" }
if ($NoSamplePlan) { $argsList += "--no-create-sample-plan" }

& $python @argsList
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
