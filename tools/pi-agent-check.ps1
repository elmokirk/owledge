[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path,
  [string]$Question = "",
  [switch]$BuildIndex,
  [switch]$SkipIndex
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = (Resolve-Path -LiteralPath $ProjectRoot).Path
$cli = Join-Path $root "tools\agent_memory_cli.py"
$python = if ($env:AGENT_MEMORY_PYTHON) { $env:AGENT_MEMORY_PYTHON } else { "python" }
if (-not (Test-Path -LiteralPath $cli)) {
  throw "Could not find tools\agent_memory_cli.py in the project root. Copy the local CLI into the project or run this check from the Owledge repo checkout."
}

function Invoke-JsonStep {
  param([string[]]$CliArgs)
  $output = & $python $cli @CliArgs
  $exit = $LASTEXITCODE
  return [pscustomobject]@{
    exit_code = $exit
    output = ($output -join "`n")
  }
}

$checks = [ordered]@{}
$checks["contract"] = Invoke-JsonStep @("--project-root", $root, "test-contracts")
$checks["validate"] = Invoke-JsonStep @("--project-root", $root, "validate-memory")
if ($BuildIndex -and -not $SkipIndex) {
  $checks["index"] = Invoke-JsonStep @("--project-root", $root, "build-memory-index")
}

$ideaDir = Join-Path $root "agent-memory\ideas"
$ideaCount = 0
if (Test-Path -LiteralPath $ideaDir) {
  $ideaCount = (Get-ChildItem -LiteralPath $ideaDir -Filter *.md -File -ErrorAction SilentlyContinue | Measure-Object).Count
}

[pscustomobject]@{
  project_root = $root
  question = $Question
  generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
  idea_count = $ideaCount
  checks = $checks
  recommended_next_questions = @(
    "Is PROJECT_CONTEXT.md current?",
    "Are there ideas matching this plan?",
    "Are validation commands known?",
    "Does every promotion candidate cite evidence?"
  )
} | ConvertTo-Json -Depth 6
