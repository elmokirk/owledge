[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path,
  [string]$ReportPath = "",
  [int]$AcceptThreshold = 85,
  [int]$PromoteThreshold = 95,
  [switch]$NoWrite
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-ProjectMeta {
  param([string]$Root)
  $meta = @{
    tenant_id = "tenant-local"
    customer_id = "customer-local"
    project_id = (Split-Path -Leaf $Root)
  }
  $projectContext = Join-Path $Root "PROJECT_CONTEXT.md"
  if (Test-Path -LiteralPath $projectContext) {
    $text = Get-Content -LiteralPath $projectContext -Raw
    foreach ($key in @("tenant_id", "customer_id", "project_id")) {
      if ($text -match "(?m)^$key`:\s*`"?([^`"\r\n]+)`"?") {
        $meta[$key] = $Matches[1].Trim()
      }
    }
  }
  return $meta
}

function Measure-Section {
  param([string]$Text, [string]$Name)
  return ($Text -match "(?m)^##\s+$([regex]::Escape($Name))\s*$")
}

function Clamp-Score {
  param([double]$Value)
  return [int][Math]::Max(1, [Math]::Min(100, [Math]::Round($Value)))
}

$root = (Resolve-Path -LiteralPath $ProjectRoot).Path
$memoryRoot = Join-Path $root "agent-memory"
if (-not (Test-Path -LiteralPath $memoryRoot)) {
  throw "No agent-memory directory found at $memoryRoot"
}

if ([string]::IsNullOrWhiteSpace($ReportPath)) {
  $reportDir = Join-Path $memoryRoot "pi-agent\reports"
  $latest = Get-ChildItem -LiteralPath $reportDir -Filter "pi-intelligence-*.md" -File -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTimeUtc -Descending |
    Select-Object -First 1
  if ($null -eq $latest) {
    throw "No PI intelligence report found. Run tools\pi-intelligence-report.ps1 first or pass -ReportPath."
  }
  $ReportPath = $latest.FullName
}

$resolvedReport = (Resolve-Path -LiteralPath $ReportPath).Path
$reportText = Get-Content -LiteralPath $resolvedReport -Raw
$relativeReport = $resolvedReport.Substring($root.Length).TrimStart("\", "/").Replace("\", "/")
$projectMeta = Get-ProjectMeta $root

$hasRequiredSections = @(
  Measure-Section $reportText "Executive Summary"
  Measure-Section $reportText "Parallel Candidates"
  Measure-Section $reportText "Trend Signals"
  Measure-Section $reportText "Recurring Agent Errors"
  Measure-Section $reportText "Central Project Candidates"
  Measure-Section $reportText "Recommended Actions"
)
$coverageScore = Clamp-Score ((($hasRequiredSections | Where-Object { $_ }).Count / 6.0) * 100)

$sourceReferences = ([regex]::Matches($reportText, "agent-memory/[^\s`)]+")).Count
$scannedArtifactSignal = if ($reportText -match "Scanned artifacts:\s+\d+") { 20 } else { 0 }
$evidenceScore = Clamp-Score ([Math]::Min(100, ($sourceReferences * 12) + $scannedArtifactSignal))

$deterministicTerms = @("problem_patterns", "architecture_patterns", "failure_modes", "concept_tags", "frontmatter", "typed edges", "Support:")
$deterministicHits = 0
foreach ($term in $deterministicTerms) {
  if ($reportText.ToLowerInvariant().Contains($term.ToLowerInvariant())) { $deterministicHits++ }
}
$determinismScore = Clamp-Score (($deterministicHits / [double]$deterministicTerms.Count) * 100)

$actionSignals = @("Recommended Actions", "Recommended fix", "Validate", "review", "promote", "QA gate", "skill rule")
$actionHits = 0
foreach ($term in $actionSignals) {
  if ($reportText.ToLowerInvariant().Contains($term.ToLowerInvariant())) { $actionHits++ }
}
$actionabilityScore = Clamp-Score (($actionHits / [double]$actionSignals.Count) * 100)

$safetyScore = 100
if ($reportText -notmatch "candidate intelligence") { $safetyScore -= 25 }
if ($reportText -match "(?i)(api[_-]?key|password|secret|bearer\s+[a-z0-9._-]+|private[_-]?key)") { $safetyScore -= 40 }
if ($reportText -match "(?i)automatically promoted|auto-promote") { $safetyScore -= 15 }
$safetyScore = Clamp-Score $safetyScore

$challengeScore = 60
if ($reportText -match "(?i)No .* reached|No .* found|threshold") { $challengeScore += 15 }
if ($reportText -match "(?i)must not be promoted|requires curator|review") { $challengeScore += 15 }
if ($reportText -match "(?i)contradiction|risk|private|confidential") { $challengeScore += 10 }
$challengeScore = Clamp-Score $challengeScore

$weighted = (
  ($coverageScore * 0.18) +
  ($evidenceScore * 0.22) +
  ($determinismScore * 0.18) +
  ($actionabilityScore * 0.17) +
  ($safetyScore * 0.15) +
  ($challengeScore * 0.10)
)
$totalScore = Clamp-Score $weighted

$recommendation = "block"
if ($totalScore -ge $PromoteThreshold) {
  $recommendation = "promote-candidate"
} elseif ($totalScore -ge $AcceptThreshold) {
  $recommendation = "accept"
} elseif ($totalScore -ge 70) {
  $recommendation = "revise"
}

$blockingIssues = @()
if ($coverageScore -lt 90) { $blockingIssues += "Missing required report sections." }
if ($evidenceScore -lt 70) { $blockingIssues += "Insufficient source references or scanned-artifact evidence." }
if ($safetyScore -lt 90) { $blockingIssues += "Safety language or sensitive-data controls are insufficient." }
if ($totalScore -lt $AcceptThreshold) { $blockingIssues += "Total score below accept threshold $AcceptThreshold." }
if ($blockingIssues.Count -eq 0) { $blockingIssues += "No blocking issue detected by the deterministic evaluator." }

$improvements = @()
if ($determinismScore -lt 85) { $improvements += "Cite deterministic fields explicitly: concept_tags, problem_patterns, architecture_patterns, failure_modes, typed edges." }
if ($actionabilityScore -lt 85) { $improvements += "Add owner-ready next actions and concrete fixes for recurring errors." }
if ($challengeScore -lt 85) { $improvements += "Challenge weak signals more directly and call out missing data, contradictions, and threshold limits." }
if ($improvements.Count -eq 0) { $improvements += "Maintain current structure; next improvement is reviewer calibration against real project outcomes." }

$now = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddHHmmss")
$runId = "$stamp-$PID-$([System.Guid]::NewGuid().ToString("N").Substring(0, 8))"
$outDir = Join-Path $memoryRoot "pi-agent\red-team"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$outPath = Join-Path $outDir "pi-redteam-evaluation-$runId.md"
$memoryId = "mem:$($projectMeta.tenant_id):$($projectMeta.customer_id):$($projectMeta.project_id):qa:pi-redteam-evaluation-$runId"

$scoreRows = @(
  "| Coverage | $coverageScore | 18 | Required PI report sections present |"
  "| Evidence quality | $evidenceScore | 22 | Source links and scanned artifact signal |"
  "| Determinism | $determinismScore | 18 | Uses frontmatter fields and typed signals |"
  "| Actionability | $actionabilityScore | 17 | Clear fixes, owners, next actions |"
  "| Safety / promotion guardrails | $safetyScore | 15 | Candidate-only language and no secret indicators |"
  "| Red-team challenge strength | $challengeScore | 10 | Calls out weak signals and risks |"
)

$report = @"
---
memory_id: "$memoryId"
tenant_id: "$($projectMeta.tenant_id)"
customer_id: "$($projectMeta.customer_id)"
project_id: "$($projectMeta.project_id)"
doc_type: "qa"
status: "draft"
visibility: "private"
data_class: "internal"
semantic_title: "PI Red Team Evaluation $runId"
summary: "Red-team evaluation of a PI Agent intelligence report. Score: $totalScore/100. Recommendation: $recommendation."
concept_tags:
  - "pi-agent"
  - "red-team"
  - "evaluation"
stack_tags: []
problem_patterns: []
architecture_patterns: []
failure_modes: []
reusable_lessons: []
confidence: 0.75
review_status: "unreviewed"
sanitization_status: "not_required"
created_at: "$now"
updated_at: "$now"
source_hash: ""
evaluated_artifact: "$relativeReport"
score_total: $totalScore
promotion_recommendation: "$recommendation"
edges: []
---

# PI Red Team Evaluation

## Verdict

Score: **$totalScore/100**

Recommendation: **$recommendation**

This evaluation challenges the PI Agent report before any finding is treated as promotion-ready.

## Scorecard

| Dimension | Score | Weight | Notes |
| --- | ---: | ---: | --- |
$($scoreRows -join "`n")

## Blocking Issues

$($blockingIssues | ForEach-Object { "- $_" } | Out-String)

## Improvement Suggestions

$($improvements | ForEach-Object { "- $_" } | Out-String)

## Evidence

- Source report: ``$relativeReport``
- Accept threshold: $AcceptThreshold
- Promote threshold: $PromoteThreshold
"@

if (-not $NoWrite) {
  $tmp = Join-Path $outDir ".$runId.tmp"
  [System.IO.File]::WriteAllText($tmp, $report, [System.Text.UTF8Encoding]::new($false))
  Move-Item -LiteralPath $tmp -Destination $outPath -Force
}

[pscustomobject]@{
  project_root = $root
  evaluated_report = $relativeReport
  evaluation_path = if ($NoWrite) { $null } else { $outPath }
  score_total = $totalScore
  recommendation = $recommendation
  dimensions = [ordered]@{
    coverage = $coverageScore
    evidence_quality = $evidenceScore
    determinism = $determinismScore
    actionability = $actionabilityScore
    safety = $safetyScore
    challenge_strength = $challengeScore
  }
  blocking_issues = $blockingIssues
  improvement_suggestions = $improvements
} | ConvertTo-Json -Depth 6
