[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [string]$TaskId,
  [string]$ProjectRoot = (Get-Location).Path,
  [string]$TenantId = "",
  [string]$CustomerId = "",
  [string]$ProjectId = "",
  [string]$Objective = "",
  [ValidateSet("orchestrator", "planner", "strategic-reviewer", "worker", "qa-agent", "memory-curator", "observer")]
  [string]$AgentRole = "worker",
  [int]$BudgetChars = 0
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "agent_memory_cli.py"
$python = if ($env:AGENT_MEMORY_PYTHON) { $env:AGENT_MEMORY_PYTHON } else { "python" }
$argsList = @($scriptPath, "--project-root", $ProjectRoot, "build-context-pack", "--task-id", $TaskId, "--agent-role", $AgentRole)
if (-not [string]::IsNullOrWhiteSpace($TenantId)) {
  $argsList += @("--tenant-id", $TenantId)
}
if (-not [string]::IsNullOrWhiteSpace($CustomerId)) {
  $argsList += @("--customer-id", $CustomerId)
}
if (-not [string]::IsNullOrWhiteSpace($ProjectId)) {
  $argsList += @("--project-id", $ProjectId)
}
if ($BudgetChars -gt 0) {
  $argsList += @("--budget-chars", [string]$BudgetChars)
}
if (-not [string]::IsNullOrWhiteSpace($Objective)) {
  $argsList += @("--objective", $Objective)
}
& $python @argsList
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
