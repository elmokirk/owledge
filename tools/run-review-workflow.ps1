[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path,
  [ValidateSet("multi-perspective-red-team", "expert-lens", "scenario-simulation", "persona-pack", "review-to-task-plan")]
  [string]$ReviewType = "",
  [string]$Subject = "",
  [string]$Question = "",
  [string]$Slug = "",
  [string]$OutputDir = "",
  [string]$TenantId = "",
  [string]$CustomerId = "",
  [string]$ProjectId = "",
  [switch]$Help
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ($Help) {
  @"
Usage:
  tools\run-review-workflow.ps1 -ReviewType <type> -Subject <path-or-memory-id> [-Question <question>]

Review types:
  multi-perspective-red-team, expert-lens, scenario-simulation, persona-pack, review-to-task-plan

Options:
  -ProjectRoot <path>  Project root. Defaults to current directory.
  -Slug <slug>         Optional stable slug seed.
  -OutputDir <path>    Optional output directory inside the project root.
  -TenantId <id>       Override tenant_id.
  -CustomerId <id>     Override customer_id.
  -ProjectId <id>      Override project_id.
"@
  exit 0
}

if ([string]::IsNullOrWhiteSpace($ReviewType)) { throw "-ReviewType is required. Use -Help for usage." }
if ([string]::IsNullOrWhiteSpace($Subject)) { throw "-Subject is required. Use -Help for usage." }

$scriptPath = Join-Path $PSScriptRoot "agent_memory_cli.py"
$python = if ($env:AGENT_MEMORY_PYTHON) { $env:AGENT_MEMORY_PYTHON } else { "python" }
$argsList = @("--project-root", $ProjectRoot, "run-review-workflow", "--review-type", $ReviewType, "--subject", $Subject)

if (-not [string]::IsNullOrWhiteSpace($Question)) { $argsList += @("--question", $Question) }
if (-not [string]::IsNullOrWhiteSpace($Slug)) { $argsList += @("--slug", $Slug) }
if (-not [string]::IsNullOrWhiteSpace($OutputDir)) { $argsList += @("--output-dir", $OutputDir) }
if (-not [string]::IsNullOrWhiteSpace($TenantId)) { $argsList += @("--tenant-id", $TenantId) }
if (-not [string]::IsNullOrWhiteSpace($CustomerId)) { $argsList += @("--customer-id", $CustomerId) }
if (-not [string]::IsNullOrWhiteSpace($ProjectId)) { $argsList += @("--project-id", $ProjectId) }

& $python $scriptPath @argsList
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
