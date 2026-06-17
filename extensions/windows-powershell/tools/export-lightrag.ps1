[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path,
  [string]$TenantId = "",
  [string]$CustomerId = "",
  [string]$ProjectId = "",
  [ValidateSet("private", "shared")]
  [string]$CorpusType = "private",
  [switch]$IncludeDrafts
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "agent_memory_cli.py"
$python = if ($env:AGENT_MEMORY_PYTHON) { $env:AGENT_MEMORY_PYTHON } else { "python" }
$argsList = @($scriptPath, "--project-root", $ProjectRoot, "export-lightrag", "--corpus-type", $CorpusType)
if (-not [string]::IsNullOrWhiteSpace($TenantId)) {
  $argsList += @("--tenant-id", $TenantId)
}
if (-not [string]::IsNullOrWhiteSpace($CustomerId)) {
  $argsList += @("--customer-id", $CustomerId)
}
if (-not [string]::IsNullOrWhiteSpace($ProjectId)) {
  $argsList += @("--project-id", $ProjectId)
}
if ($IncludeDrafts) { $argsList += "--include-drafts" }
& $python @argsList
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
