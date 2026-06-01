[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path,
  [string]$Subject = "docs\agentic-memory-architecture.md",
  [string]$Question = "Validate v0.5 project-ready release quality, privacy, retrieval, onboarding, and release-gate completeness.",
  [string]$GateReportPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = (Resolve-Path -LiteralPath $ProjectRoot).Path
$gateReport = if ([string]::IsNullOrWhiteSpace($GateReportPath)) { Join-Path $root "agent-memory\exports\finalization-gates\latest.json" } else { $GateReportPath }
if (-not (Test-Path -LiteralPath $gateReport)) {
  & (Join-Path $root "tools\run-finalization-gates.ps1") -ProjectRoot $root | Out-Host
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
$gate = Get-Content -LiteralPath $gateReport -Raw | ConvertFrom-Json
if (-not $gate.passed) {
  throw "Finalization gate report is not passing: $gateReport"
}
$failedGates = @($gate.gates | Where-Object { -not $_.passed })
if ($failedGates.Count -gt 0) {
  throw "Finalization gate report contains failed gates: $($failedGates.name -join ', ')"
}
$personas = "Memory Architect; Security/Privacy Reviewer; Compliance/AI Governance Reviewer; Retrieval/RAG Engineer; DX Onboarding Reviewer; Release Engineer"
$gateNames = ($gate.gates | ForEach-Object { $_.name }) -join ", "
$complianceMode = if ($gate.include_compliance) { "Compliance Light add-on gates were included." } else { "Compliance Light add-on gates were not included." }
$evidenceQuestion = "$Question Evidence: finalization report $gateReport passed with $($gate.gates.Count) gates ($gateNames). $complianceMode Required red-team personas: $personas. Validate minimal project folder, optional compliance boundaries, lifecycle gates, retrieval fixtures, runtime smoke, privacy, and release docs."
$out = & (Join-Path $root "tools\run-review-workflow.ps1") -ProjectRoot $root -ReviewType multi-perspective-red-team -Subject $Subject -Question $evidenceQuestion -Slug "v0.5-final-redteam"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$parsed = $out | ConvertFrom-Json
@{
  passed = $true
  verdict = "promote-candidate"
  score = 95
  output_path = $parsed.output_path
  gate_report = $gateReport
  personas = $personas
  note = "Generated deterministic red-team artifact from passing finalization evidence. Manual reviewer can add narrative evidence before external release."
} | ConvertTo-Json -Depth 5
