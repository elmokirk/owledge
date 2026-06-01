[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path,
  [int]$MinSupport = 2,
  [switch]$NoWrite
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-Slug {
  param([string]$Value)
  $slug = ($Value.ToLowerInvariant() -replace '[^a-z0-9]+','-').Trim('-')
  if ([string]::IsNullOrWhiteSpace($slug)) { return "signal" }
  return $slug
}

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

function Read-MemoryMeta {
  param([string]$Path)
  $text = Get-Content -LiteralPath $Path -Raw
  if ($text -notmatch "(?s)^---\r?\n(.*?)\r?\n---") { return $null }
  $frontmatter = $Matches[1]
  $lines = $frontmatter -split "\r?\n"
  $meta = @{}
  for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    if ($line -match "^([A-Za-z0-9_-]+):\s*(.*)$") {
      $key = $Matches[1]
      $value = $Matches[2].Trim()
      if ($value -eq "") {
        $items = @()
        $j = $i + 1
        while ($j -lt $lines.Count -and $lines[$j] -match "^\s+-\s+(.+)$") {
          $items += (($Matches[1].Trim()) -replace '^"|"$','')
          $j++
        }
        $meta[$key] = $items
      } else {
        $meta[$key] = ($value -replace '^"|"$','')
      }
    }
  }
  return $meta
}

function Add-Count {
  param(
    [hashtable]$Map,
    [string]$Key,
    [object]$Doc
  )
  if ([string]::IsNullOrWhiteSpace($Key)) { return }
  if (-not $Map.ContainsKey($Key)) { $Map[$Key] = New-Object System.Collections.ArrayList }
  [void]$Map[$Key].Add($Doc)
}

function Format-SourceList {
  param([object[]]$Docs)
  $items = @()
  foreach ($doc in ($Docs | Select-Object -First 6)) {
    $items += "- `$($doc.path)` - $($doc.title) [$($doc.doc_type)]"
  }
  if ($items.Count -eq 0) { return "- No sources found." }
  return ($items -join "`n")
}

$root = (Resolve-Path -LiteralPath $ProjectRoot).Path
$memoryRoot = Join-Path $root "agent-memory"
if (-not (Test-Path -LiteralPath $memoryRoot)) {
  throw "No agent-memory directory found at $memoryRoot"
}

$projectMeta = Get-ProjectMeta $root
$docs = @()
$excluded = @("\templates\", "\exports\", "\indexes\", "\pi-agent\reports\", "\pi-agent\red-team\", "\pi-agent\evaluations\", "\pi-agent\scorecards\")

Get-ChildItem -LiteralPath $memoryRoot -Recurse -Filter *.md -File | ForEach-Object {
  $path = $_.FullName
  $relative = $path.Substring($root.Length).TrimStart("\", "/").Replace("\", "/")
  foreach ($part in $excluded) {
    if ($path.Contains($part)) { return }
  }
  $meta = Read-MemoryMeta $path
  if ($null -eq $meta) { return }
  $docs += [pscustomobject]@{
    path = $relative
    memory_id = $meta["memory_id"]
    doc_type = $meta["doc_type"]
    status = $meta["status"]
    review_status = $meta["review_status"]
    title = if ($meta.ContainsKey("semantic_title")) { $meta["semantic_title"] } else { $_.BaseName }
    summary = if ($meta.ContainsKey("summary")) { $meta["summary"] } else { "" }
    concept_tags = @($meta["concept_tags"])
    problem_patterns = @($meta["problem_patterns"])
    architecture_patterns = @($meta["architecture_patterns"])
    failure_modes = @($meta["failure_modes"])
  }
}

$tagMap = @{}
$problemMap = @{}
$architectureMap = @{}
$failureMap = @{}

foreach ($doc in $docs) {
  foreach ($item in $doc.concept_tags) { Add-Count $tagMap $item $doc }
  foreach ($item in $doc.problem_patterns) { Add-Count $problemMap $item $doc }
  foreach ($item in $doc.architecture_patterns) { Add-Count $architectureMap $item $doc }
  foreach ($item in $doc.failure_modes) { Add-Count $failureMap $item $doc }
}

function Select-Signals {
  param([hashtable]$Map, [int]$Min)
  return $Map.Keys |
    Where-Object { $Map[$_].Count -ge $Min } |
    Sort-Object @{ Expression = { $Map[$_].Count }; Descending = $true }, @{ Expression = { $_ }; Ascending = $true }
}

$tagSignals = @(Select-Signals $tagMap $MinSupport)
$problemSignals = @(Select-Signals $problemMap $MinSupport)
$architectureSignals = @(Select-Signals $architectureMap $MinSupport)
$failureSignals = @(Select-Signals $failureMap $MinSupport)
$now = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddHHmmss")
$runId = "$stamp-$PID-$([System.Guid]::NewGuid().ToString("N").Substring(0, 8))"
$reportDir = Join-Path $memoryRoot "pi-agent\reports"
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
$reportPath = Join-Path $reportDir "pi-intelligence-$runId.md"
$memoryId = "mem:$($projectMeta.tenant_id):$($projectMeta.customer_id):$($projectMeta.project_id):qa:pi-intelligence-$runId"

$parallelLines = @()
foreach ($signal in ($problemSignals + $architectureSignals + $tagSignals | Select-Object -Unique | Select-Object -First 20)) {
  $sourceDocs = @()
  if ($problemMap.ContainsKey($signal)) { $sourceDocs += $problemMap[$signal] }
  if ($architectureMap.ContainsKey($signal)) { $sourceDocs += $architectureMap[$signal] }
  if ($tagMap.ContainsKey($signal)) { $sourceDocs += $tagMap[$signal] }
  $sourceDocs = @($sourceDocs | Select-Object -Unique -Property path, title, doc_type)
  $parallelLines += "### $signal`n`nSupport: $($sourceDocs.Count) sources.`n`n$(Format-SourceList $sourceDocs)`n"
}
$parallelCandidateCount = $parallelLines.Count
if ($parallelLines.Count -eq 0) { $parallelLines = @("No parallel candidates met MinSupport=$MinSupport.") }

$trendLines = @()
foreach ($signal in ($tagSignals | Select-Object -First 12)) {
  $trendLines += "- `$signal` appears in $($tagMap[$signal].Count) artifacts."
}
foreach ($signal in ($problemSignals | Select-Object -First 12)) {
  $trendLines += "- `$signal` appears as a problem pattern in $($problemMap[$signal].Count) artifacts."
}
$trendSignalCount = $trendLines.Count
if ($trendLines.Count -eq 0) { $trendLines = @("- No trend reached MinSupport=$MinSupport yet.") }

$errorLines = @()
foreach ($signal in ($failureSignals | Select-Object -First 20)) {
  $errorLines += "### $signal`n`nObserved in $($failureMap[$signal].Count) artifacts.`n`n$(Format-SourceList @($failureMap[$signal]))`n`nRecommended fix: convert the repeated failure into a checklist, skill rule, validation command, or QA gate before the next similar task.`n"
}
$recurringErrorSignalCount = $failureSignals.Count
if ($errorLines.Count -eq 0) { $errorLines = @("No recurring failure mode reached MinSupport=$MinSupport.") }

$centralLines = @()
foreach ($signal in ($problemSignals + $architectureSignals | Select-Object -Unique | Select-Object -First 12)) {
  $sourceDocs = @()
  if ($problemMap.ContainsKey($signal)) { $sourceDocs += $problemMap[$signal] }
  if ($architectureMap.ContainsKey($signal)) { $sourceDocs += $architectureMap[$signal] }
  $ideaDocs = @($sourceDocs | Where-Object { $_.doc_type -eq "idea" })
  if ($ideaDocs.Count -gt 0 -or $sourceDocs.Count -ge ($MinSupport + 1)) {
    $centralLines += "### Central candidate: $signal`n`nWhy: repeated source signal across $($sourceDocs.Count) memory artifacts. Validate whether this should become a reusable internal project, offer, package, or platform capability.`n`n$(Format-SourceList @($sourceDocs))`n"
  }
}
$centralProjectCandidateCount = $centralLines.Count
if ($centralLines.Count -eq 0) { $centralLines = @("No central project candidate reached the current threshold.") }

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
semantic_title: "PI Intelligence Report $runId"
summary: "Candidate intelligence report across Agent Memory for parallels, trends, recurring agent errors, and central project opportunities."
concept_tags:
  - "pi-agent"
  - "intelligence-report"
  - "cross-project-intelligence"
stack_tags: []
problem_patterns: []
architecture_patterns: []
failure_modes: []
reusable_lessons: []
confidence: 0.7
review_status: "unreviewed"
sanitization_status: "not_required"
created_at: "$now"
updated_at: "$now"
source_hash: ""
edges: []
---

# PI Intelligence Report

Generated: $now

## Executive Summary

- Scanned artifacts: $($docs.Count)
- Parallel signals: $parallelCandidateCount
- Trend signals: $trendSignalCount
- Recurring error signals: $recurringErrorSignalCount
- Central project candidates: $centralProjectCandidateCount

This report is candidate intelligence. It must not be promoted into canonical memory without curator or owner review.

## Parallel Candidates

$($parallelLines -join "`n")

## Trend Signals

$($trendLines -join "`n")

## Recurring Agent Errors

$($errorLines -join "`n")

## Central Project Candidates

$($centralLines -join "`n")

## Recommended Actions

1. Review recurring failure modes and turn confirmed ones into QA gates or skill rules.
2. Promote confirmed parallels into ``agent-memory/patterns/`` or ``agent-memory/lessons/``.
3. Convert high-signal central project candidates into idea cards or planning specs.
4. Re-run this report after major planning, compaction, or memory promotion.
"@

if (-not $NoWrite) {
  $tmp = Join-Path $reportDir ".$runId.tmp"
  [System.IO.File]::WriteAllText($tmp, $report, [System.Text.UTF8Encoding]::new($false))
  Move-Item -LiteralPath $tmp -Destination $reportPath -Force
}

[pscustomobject]@{
  project_root = $root
  report_path = if ($NoWrite) { $null } else { $reportPath }
  scanned_artifacts = $docs.Count
  parallel_signal_count = $parallelCandidateCount
  trend_signal_count = $trendSignalCount
  recurring_error_signal_count = $recurringErrorSignalCount
  central_project_candidate_count = $centralProjectCandidateCount
  min_support = $MinSupport
} | ConvertTo-Json -Depth 5
