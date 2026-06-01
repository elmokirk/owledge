[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path,
  [ValidateSet("decision", "handoff", "rag-readiness", "agent-activity", "project-dashboard", "website-ui")]
  [string]$ReportType = "project-dashboard",
  [string]$OutputDir = "",
  [string]$Title = "",
  [ValidateSet("private", "customer", "shared")]
  [string]$Audience = "private",
  [string]$TenantId = "",
  [string]$CustomerId = "",
  [string]$ProjectId = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "agent_memory_cli.py"
$python = if ($env:AGENT_MEMORY_PYTHON) { $env:AGENT_MEMORY_PYTHON } else { "python" }
$argsList = @("--project-root", $ProjectRoot, "render-memory-report", "--report-type", $ReportType)
$argsList += @("--audience", $Audience)
if ($OutputDir) {
  $argsList += @("--output-dir", $OutputDir)
}
if ($Title) {
  $argsList += @("--title", $Title)
}
if (-not [string]::IsNullOrWhiteSpace($TenantId)) { $argsList += @("--tenant-id", $TenantId) }
if (-not [string]::IsNullOrWhiteSpace($CustomerId)) { $argsList += @("--customer-id", $CustomerId) }
if (-not [string]::IsNullOrWhiteSpace($ProjectId)) { $argsList += @("--project-id", $ProjectId) }

& $python $scriptPath @argsList
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
