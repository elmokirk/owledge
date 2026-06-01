[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path,
  [Parameter(Mandatory=$true)][string]$Title,
  [Parameter(Mandatory=$true)][string]$Summary,
  [string]$Source = "agent-session",
  [string[]]$ConceptTags = @("idea"),
  [string[]]$ProblemPatterns = @(),
  [string[]]$ArchitecturePatterns = @()
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Slugify {
  param([string]$Value)
  $slug = ($Value.ToLowerInvariant() -replace '[^a-z0-9]+','-').Trim('-')
  if ([string]::IsNullOrWhiteSpace($slug)) { return "idea" }
  return $slug
}

function YamlList {
  param([string[]]$Values)
  if (-not $Values -or $Values.Count -eq 0) { return "[]" }
  return ($Values | ForEach-Object { "  - `"$($_ -replace '"','\"')`"" }) -join "`n"
}

$root = (Resolve-Path -LiteralPath $ProjectRoot).Path
$projectContext = Join-Path $root "PROJECT_CONTEXT.md"
$projectId = Split-Path -Leaf $root
$tenantId = "tenant-local"
$customerId = "customer-local"
if (Test-Path -LiteralPath $projectContext) {
  $text = Get-Content -LiteralPath $projectContext -Raw
  if ($text -match '(?m)^tenant_id:\s*"?([^"\r\n]+)"?') { $tenantId = $Matches[1].Trim() }
  if ($text -match '(?m)^customer_id:\s*"?([^"\r\n]+)"?') { $customerId = $Matches[1].Trim() }
  if ($text -match '(?m)^project_id:\s*"?([^"\r\n]+)"?') { $projectId = $Matches[1].Trim() }
}

$slug = Slugify $Title
$now = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddHHmmss")
$random = [System.Guid]::NewGuid().ToString("N").Substring(0, 8)
$uniqueSlug = "$slug-$stamp-$random"
$ideasDir = Join-Path $root "agent-memory\ideas"
New-Item -ItemType Directory -Force -Path $ideasDir | Out-Null
$path = Join-Path $ideasDir "$uniqueSlug.md"

$memoryId = "mem:$tenantId`:$customerId`:$projectId`:idea:$uniqueSlug"
$body = @"
---
memory_id: "$memoryId"
tenant_id: "$tenantId"
customer_id: "$customerId"
project_id: "$projectId"
doc_type: "idea"
status: "draft"
visibility: "private"
data_class: "internal"
semantic_title: "$Title"
summary: "$Summary"
concept_tags:
$(YamlList $ConceptTags)
stack_tags: []
problem_patterns:
$(YamlList $ProblemPatterns)
architecture_patterns:
$(YamlList $ArchitecturePatterns)
failure_modes: []
reusable_lessons: []
confidence: 0.4
review_status: "unreviewed"
sanitization_status: "not_required"
created_at: "$now"
updated_at: "$now"
source_hash: ""
idea_stage: "captured"
idea_source: "$Source"
planning_relevance:
  - "check-before-new-plan"
edges: []
---

# $Title

## Idea

$Summary

## Trigger

$Source

## Similar Ideas / Existing Work

- Check `agent-memory/ideas/`, `agent-memory/patterns/`, `agent-memory/lessons/`, and ADRs before planning.

## Next Action

Triage this idea and decide whether it becomes a task, ADR, pattern, lesson, or new project proposal.
"@

$tmp = Join-Path $ideasDir ".$uniqueSlug.tmp"
[System.IO.File]::WriteAllText($tmp, $body, [System.Text.UTF8Encoding]::new($false))
Move-Item -LiteralPath $tmp -Destination $path -Force
[pscustomobject]@{ path = $path; memory_id = $memoryId; status = "captured" } | ConvertTo-Json
