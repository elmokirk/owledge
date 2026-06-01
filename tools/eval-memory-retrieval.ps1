[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path,
  [Parameter(Mandatory=$true)]
  [string[]]$ProjectRoots,
  [string]$OutputDir = "",
  [string]$QueriesFile = "",
  [int]$TopK = 5,
  [double]$MinOverallScore = -1,
  [double]$MinSafetyScore = -1,
  [switch]$IncludeSessions
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "agent_memory_cli.py"
$python = if ($env:AGENT_MEMORY_PYTHON) { $env:AGENT_MEMORY_PYTHON } else { "python" }
$normalizedProjectRoots = @()
foreach ($entry in $ProjectRoots) {
  $normalizedProjectRoots += ([string]$entry).Split(",") | Where-Object { $_.Trim() } | ForEach-Object { $_.Trim() }
}
$argsList = @("--project-root", $ProjectRoot, "eval-memory-retrieval", "--project-roots") + $normalizedProjectRoots + @("--top-k", [string]$TopK)
if ($OutputDir) {
  $argsList += @("--output-dir", $OutputDir)
}
if ($QueriesFile) {
  $argsList += @("--queries-file", $QueriesFile)
}
if ($MinOverallScore -ge 0) {
  $argsList += @("--min-overall-score", [string]$MinOverallScore)
}
if ($MinSafetyScore -ge 0) {
  $argsList += @("--min-safety-score", [string]$MinSafetyScore)
}
if ($IncludeSessions) {
  $argsList += "--include-sessions"
}

& $python $scriptPath @argsList
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
