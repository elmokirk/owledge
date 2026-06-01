[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [string]$TenantId,
  [Parameter(Mandatory = $true)]
  [string]$CustomerId,
  [Parameter(Mandatory = $true)]
  [string]$ProjectId,
  [Parameter(Mandatory = $true)]
  [string]$SourcePath,
  [Parameter(Mandatory = $true)]
  [string]$TargetPath,
  [Parameter(Mandatory = $true)]
  [string]$ReviewPath,
  [string]$SourceHash = "",
  [string]$AgentId = "cli-curator",
  [string]$ProjectRoot = (Get-Location).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "agent_memory_cli.py"
$python = if ($env:AGENT_MEMORY_PYTHON) { $env:AGENT_MEMORY_PYTHON } else { "python" }
$argsList = @($scriptPath, "--project-root", $ProjectRoot, "promote", "--tenant-id", $TenantId, "--customer-id", $CustomerId, "--project-id", $ProjectId, "--source-path", $SourcePath, "--target-path", $TargetPath, "--review-path", $ReviewPath, "--agent-id", $AgentId)
if (-not [string]::IsNullOrWhiteSpace($SourceHash)) {
  $argsList += @("--source-hash", $SourceHash)
}
& $python @argsList
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
