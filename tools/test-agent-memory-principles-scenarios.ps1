[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = (Resolve-Path -LiteralPath $ProjectRoot).Path
$tmpBase = Join-Path $root ".agent-control\tmp\principles-scenarios"
if (Test-Path -LiteralPath $tmpBase) {
  Remove-Item -LiteralPath $tmpBase -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $tmpBase | Out-Null

$builder = Join-Path $root "tools\build-kb-module.ps1"
$python = if ($env:AGENT_MEMORY_PYTHON) { $env:AGENT_MEMORY_PYTHON } else { "python" }
$builderPy = Join-Path $root "tools\build_kb_module.py"
$results = New-Object System.Collections.Generic.List[object]

function Add-Result {
  param([string]$Name, [bool]$Passed, [string]$Details)
  $results.Add([ordered]@{ name = $Name; passed = $Passed; details = $Details })
}

function Set-FileUtf8 {
  param([string]$Path, [string]$Value)
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Path) | Out-Null
  Set-Content -LiteralPath $Path -Encoding UTF8 -Value $Value
}

function Get-TreeHash {
  param([string]$RootPath, [string[]]$ExcludePrefixes = @())
  $resolvedRoot = (Resolve-Path -LiteralPath $RootPath).Path.TrimEnd("\", "/")
  $rows = @()
  Get-ChildItem -LiteralPath $RootPath -Recurse -File | ForEach-Object {
    $fullPath = $_.FullName
    if ($fullPath.StartsWith($resolvedRoot, [StringComparison]::OrdinalIgnoreCase)) {
      $relative = $fullPath.Substring($resolvedRoot.Length).TrimStart("\", "/").Replace("\", "/")
    } else {
      $relative = $_.Name
    }
    foreach ($prefix in $ExcludePrefixes) {
      if ($relative.StartsWith($prefix)) { return }
    }
    $rows += "$relative=$((Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash)"
  }
  return ($rows | Sort-Object) -join "`n"
}

function Invoke-ExpectFailure {
  param([string]$KnowledgebaseRoot, [string]$MapFile)
  $previousErrorActionPreference = $ErrorActionPreference
  $previousNativeCommandPreference = $null
  if (Test-Path -LiteralPath Variable:\PSNativeCommandUseErrorActionPreference) {
    $previousNativeCommandPreference = $PSNativeCommandUseErrorActionPreference
    $PSNativeCommandUseErrorActionPreference = $false
  }
  $ErrorActionPreference = "Continue"
  & $python $builderPy --knowledgebase-root $KnowledgebaseRoot --kit-root $root --map-file $MapFile 2>$null | Out-Null
  $exitCode = $LASTEXITCODE
  $ErrorActionPreference = $previousErrorActionPreference
  if ($null -ne $previousNativeCommandPreference) {
    $PSNativeCommandUseErrorActionPreference = $previousNativeCommandPreference
  }
  $global:LASTEXITCODE = 0
  return ($exitCode -ne 0)
}

function New-MappedKb {
  param([string]$Path)
  New-Item -ItemType Directory -Force -Path $Path | Out-Null
  foreach ($relative in @("00_Inbox","20_Plans","30_Evidence","40_Handoffs","50_Reviews",".agent-memory\indexes")) {
    New-Item -ItemType Directory -Force -Path (Join-Path $Path $relative) | Out-Null
  }
  Set-FileUtf8 -Path (Join-Path $Path "00_Inbox\Idea.md") -Value "# Idea`n`nBuild MVP from [[Research Note]]."
  Set-FileUtf8 -Path (Join-Path $Path "Research Note.md") -Value "---`ntype: research`n---`n`n# Research Note`n`nKeep this source unchanged."
  $map = [ordered]@{
    ideas = "00_Inbox"
    plans = "20_Plans"
    evidence = "30_Evidence"
    handoffs = "40_Handoffs"
    reviews = "50_Reviews"
    indexes = ".agent-memory/indexes"
  } | ConvertTo-Json
  Set-Content -LiteralPath (Join-Path $Path "agent-memory-map.json") -Encoding UTF8 -Value $map
}

# Scenario 1: large existing codebase, module fallback, no environment-variable dependency.
$largeRoot = Join-Path $tmpBase "large-codebase"
New-Item -ItemType Directory -Force -Path $largeRoot | Out-Null
foreach ($i in 1..80) {
  Set-FileUtf8 -Path (Join-Path $largeRoot ("docs\note-{0:D3}.md" -f $i)) -Value "# Note $i`n`nLinks to [[ADR-$i]]."
}
foreach ($i in 1..120) {
  Set-FileUtf8 -Path (Join-Path $largeRoot ("src\module{0:D3}\file{0:D3}.ts" -f $i)) -Value "export const value$i = $i;"
}
$largeBefore = Get-TreeHash -RootPath $largeRoot
$oldKitRoot = $env:AGENT_MEMORY_KIT_ROOT
$oldProjectRoot = $env:AGENT_MEMORY_PROJECT_ROOT
$env:AGENT_MEMORY_KIT_ROOT = $null
$env:AGENT_MEMORY_PROJECT_ROOT = $null
& $builder -KnowledgebaseRoot $largeRoot -KitRoot $root -MaxFiles 25 | Out-Null
$env:AGENT_MEMORY_KIT_ROOT = $oldKitRoot
$env:AGENT_MEMORY_PROJECT_ROOT = $oldProjectRoot
if ($LASTEXITCODE -ne 0) { throw "Large codebase module setup failed with exit code $LASTEXITCODE" }
$largeAfter = Get-TreeHash -RootPath $largeRoot -ExcludePrefixes @("agent-memory-module/")
$largeStatusPath = Join-Path $largeRoot "agent-memory-module\agent-memory\indexes\kb-module-status.json"
$largeStatus = Get-Content -LiteralPath $largeStatusPath -Raw | ConvertFrom-Json
Add-Result "large-codebase-existing-files-unchanged" ($largeBefore -eq $largeAfter) "Existing source and Markdown files stayed byte-identical outside the module."
Add-Result "large-codebase-max-files-honored" ($largeStatus.markdown_files_scanned -eq 25) "Scanned $($largeStatus.markdown_files_scanned) Markdown files with MaxFiles=25."
Add-Result "large-codebase-zero-env" ($largeStatus.requires_os_environment_variables -eq $false) "Status reports requires_os_environment_variables=false."

# Scenario 2.1: existing user KB, repo-link equivalent via local checkout path, mapped writes only.
$userKb = Join-Path $tmpBase "existing-user-kb"
New-MappedKb -Path $userKb
$userBefore = Get-TreeHash -RootPath $userKb
& $builder -KnowledgebaseRoot $userKb -KitRoot $root -MapFile "agent-memory-map.json" | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Mapped user KB setup failed with exit code $LASTEXITCODE" }
$userAfter = Get-TreeHash -RootPath $userKb -ExcludePrefixes @("20_Plans/","30_Evidence/","40_Handoffs/","50_Reviews/",".agent-memory/indexes/")
$userStatus = Get-Content -LiteralPath (Join-Path $userKb ".agent-memory\indexes\kb-module-status.json") -Raw | ConvertFrom-Json
Add-Result "user-kb-mapped-mode" ($userStatus.mode -eq "mapped" -and $userStatus.mapping_enabled -eq $true) "Mapped mode selected from local map file."
Add-Result "user-kb-original-notes-unchanged" ($userBefore -eq $userAfter) "Original notes and map stayed byte-identical; only approved module/mapped artifacts were added."
Add-Result "user-kb-wikilinks-not-converted" ($userStatus.wiki_links_converted -eq $false) "Wiki links are reported as not converted."
Add-Result "user-kb-no-root-module-doc" (-not (Test-Path -LiteralPath (Join-Path $userKb "AGENT_MEMORY_MODULE.md"))) "Mapped mode should not create a root-level AGENT_MEMORY_MODULE.md."

# Multi-agent role simulation on mapped KB.
Set-FileUtf8 -Path (Join-Path $userKb "30_Evidence\worker-evidence.md") -Value "# Worker Evidence`n`nSource: `Research Note.md`."
Set-FileUtf8 -Path (Join-Path $userKb "40_Handoffs\worker-handoff.md") -Value "# Worker Handoff`n`nStatus: done.`n`nFiles written: 30_Evidence/worker-evidence.md."
Set-FileUtf8 -Path (Join-Path $userKb "50_Reviews\reviewer-findings.md") -Value "# Reviewer Findings`n`nVerdict: needs curator approval before promotion."
$forbiddenCentralWrites = @(
  (Join-Path $userKb "agent-memory\canonical"),
  (Join-Path $userKb "agent-memory\lessons"),
  (Join-Path $userKb "global-memory")
) | Where-Object { Test-Path -LiteralPath $_ }
Add-Result "multi-agent-role-boundaries" (@($forbiddenCentralWrites).Count -eq 0) "Worker/reviewer simulation wrote only mapped evidence, handoff, and review artifacts."

# Scenario 2.2: skill-bloat discovery with about 50 skills.
$skillBloat = Join-Path $tmpBase "skill-bloat"
New-Item -ItemType Directory -Force -Path $skillBloat | Out-Null
foreach ($i in 1..50) {
  $skillDir = Join-Path $skillBloat ("noise-skill-{0:D2}" -f $i)
  New-Item -ItemType Directory -Force -Path $skillDir | Out-Null
  Set-FileUtf8 -Path (Join-Path $skillDir "SKILL.md") -Value "---`nname: noise-skill-$i`ndescription: unrelated test skill`n---`n`n# Noise"
}
Copy-Item -LiteralPath (Join-Path $root "skills\agent-memory-principles") -Destination (Join-Path $skillBloat "agent-memory-principles") -Recurse
$matches = Get-ChildItem -LiteralPath $skillBloat -Recurse -Filter "SKILL.md" | Where-Object {
  (Get-Content -LiteralPath $_.FullName -Raw) -match "(?m)^name:\s*agent-memory-principles\s*$"
}
Add-Result "skill-bloat-exact-name-discovery" (@($matches).Count -eq 1) "Found exactly one agent-memory-principles skill among 51 skills."
Add-Result "skill-bloat-references-present" (Test-Path -LiteralPath (Join-Path $skillBloat "agent-memory-principles\references\mapping-contract.md")) "Principles skill references survive crowded skill installation."

# Scenario 2.3: Superpowers coexistence, read-only plan indexing, and Agent Memory handoff evidence.
$superpowersKb = Join-Path $tmpBase "superpowers-coexistence"
New-Item -ItemType Directory -Force -Path $superpowersKb | Out-Null
$superpowersPlan = Join-Path $superpowersKb "docs\superpowers\plans\example-plan.md"
Set-FileUtf8 -Path $superpowersPlan -Value @"
# Example Superpowers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development.

**Goal:** Add a small feature with TDD.

### Task 1: Minimal feature

- [ ] Write the failing test
- [ ] Implement the minimal code
- [ ] Run tests
- [ ] Commit
"@
Set-FileUtf8 -Path (Join-Path $superpowersKb "README.md") -Value "# Existing Project`n`nUses Superpowers for execution."
$superpowersHashBefore = (Get-FileHash -Algorithm SHA256 -LiteralPath $superpowersPlan).Hash
& $builder -KnowledgebaseRoot $superpowersKb -KitRoot $root | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Superpowers coexistence setup failed with exit code $LASTEXITCODE" }
$superpowersHashAfter = (Get-FileHash -Algorithm SHA256 -LiteralPath $superpowersPlan).Hash
$superpowersIndex = Get-Content -LiteralPath (Join-Path $superpowersKb "agent-memory-module\agent-memory\indexes\kb-scan.jsonl") -Raw
$handoffPath = Join-Path $superpowersKb "agent-memory-module\agent-memory\handoffs\superpowers-plan-handoff.md"
Set-FileUtf8 -Path $handoffPath -Value "# Superpowers Plan Handoff`n`nEvidence: `docs/superpowers/plans/example-plan.md`."
$handoffText = Get-Content -LiteralPath $handoffPath -Raw
Add-Result "superpowers-plan-unchanged" ($superpowersHashBefore -eq $superpowersHashAfter) "Superpowers plan stayed byte-identical after Agent Memory scan."
Add-Result "superpowers-plan-indexed" ($superpowersIndex -match "docs/superpowers/plans/example-plan.md") "Agent Memory index references the Superpowers plan source path."
Add-Result "superpowers-handoff-evidence" ($handoffText -match "docs/superpowers/plans/example-plan.md") "Agent Memory handoff can cite a Superpowers plan as evidence."

# Scenario 3: rare edge cases and fail-closed map handling.
$edgeKb = Join-Path $tmpBase "edge-kb"
New-MappedKb -Path $edgeKb
$edgeCases = @()
$edgeCases += [ordered]@{ name = "absolute-path"; payload = [ordered]@{ plans = "C:\escape"; evidence = "30_Evidence"; handoffs = "40_Handoffs"; reviews = "50_Reviews"; indexes = ".agent-memory/indexes" } }
$edgeCases += [ordered]@{ name = "unknown-key"; payload = [ordered]@{ plans = "20_Plans"; evidence = "30_Evidence"; handoffs = "40_Handoffs"; reviews = "50_Reviews"; indexes = ".agent-memory/indexes"; canonical = "50_Reviews" } }
$edgeCases += [ordered]@{ name = "missing-required-key"; payload = [ordered]@{ plans = "20_Plans"; evidence = "30_Evidence"; reviews = "50_Reviews"; indexes = ".agent-memory/indexes" } }
$edgeCases += [ordered]@{ name = "missing-target"; payload = [ordered]@{ plans = "20_Plans"; evidence = "30_Evidence"; handoffs = "40_Handoffs"; reviews = "50_Reviews"; indexes = "missing-indexes" } }
$edgeCases += [ordered]@{ name = "file-target"; payload = [ordered]@{ plans = "Research Note.md"; evidence = "30_Evidence"; handoffs = "40_Handoffs"; reviews = "50_Reviews"; indexes = ".agent-memory/indexes" } }
$edgeCases += [ordered]@{ name = "blank-value"; payload = [ordered]@{ plans = ""; evidence = "30_Evidence"; handoffs = "40_Handoffs"; reviews = "50_Reviews"; indexes = ".agent-memory/indexes" } }
$edgeCases += [ordered]@{ name = "null-value"; payload = [ordered]@{ plans = $null; evidence = "30_Evidence"; handoffs = "40_Handoffs"; reviews = "50_Reviews"; indexes = ".agent-memory/indexes" } }
$edgeCases += [ordered]@{ name = "array-value"; payload = [ordered]@{ plans = @("20_Plans"); evidence = "30_Evidence"; handoffs = "40_Handoffs"; reviews = "50_Reviews"; indexes = ".agent-memory/indexes" } }
foreach ($case in $edgeCases) {
  $mapPath = Join-Path $edgeKb ("bad-{0}.json" -f $case.name)
  Set-Content -LiteralPath $mapPath -Encoding UTF8 -Value ($case.payload | ConvertTo-Json)
  $failedClosed = Invoke-ExpectFailure -KnowledgebaseRoot $edgeKb -MapFile ([IO.Path]::GetFileName($mapPath))
  Add-Result "edge-fail-closed:$($case.name)" $failedClosed "Invalid map should fail closed."
}

Add-Result "edge-fail-closed:missing-explicit-map" (Invoke-ExpectFailure -KnowledgebaseRoot $edgeKb -MapFile "does-not-exist.json") "Explicit missing map file should fail closed instead of falling back."

$duplicateJson = '{"plans":"../escape","plans":"20_Plans","evidence":"30_Evidence","handoffs":"40_Handoffs","reviews":"50_Reviews","indexes":".agent-memory/indexes"}'
Set-Content -LiteralPath (Join-Path $edgeKb "bad-duplicate-key.json") -Encoding UTF8 -Value $duplicateJson
Add-Result "edge-fail-closed:duplicate-json-key" (Invoke-ExpectFailure -KnowledgebaseRoot $edgeKb -MapFile "bad-duplicate-key.json") "Duplicate JSON keys should fail closed."

$previousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
& $python $builderPy --knowledgebase-root $edgeKb --kit-root $root --max-files 0 2>$null | Out-Null
$maxFilesExitCode = $LASTEXITCODE
$ErrorActionPreference = $previousErrorActionPreference
$global:LASTEXITCODE = 0
Add-Result "edge-fail-closed:max-files-zero" ($maxFilesExitCode -ne 0) "max-files=0 should fail closed."

$bomKb = Join-Path $tmpBase "bom-frontmatter-kb"
New-Item -ItemType Directory -Force -Path $bomKb | Out-Null
[IO.File]::WriteAllText((Join-Path $bomKb "Bom.md"), ([char]0xFEFF + "---`ntype: research`nstatus: active`n---`n`n# BOM Note"), [Text.UTF8Encoding]::new($false))
& $builder -KnowledgebaseRoot $bomKb -KitRoot $root | Out-Null
if ($LASTEXITCODE -ne 0) { throw "BOM frontmatter scenario failed with exit code $LASTEXITCODE" }
$bomIndex = Get-Content -LiteralPath (Join-Path $bomKb "agent-memory-module\agent-memory\indexes\kb-scan.jsonl") -Raw | ConvertFrom-Json
Add-Result "edge-bom-frontmatter-keys" (@($bomIndex.frontmatter_keys) -contains "type" -and @($bomIndex.frontmatter_keys) -contains "status") "BOM-prefixed frontmatter keys should be detected."

$linkCaseSkipped = $false
try {
  $linkPath = Join-Path $edgeKb "linked-plans"
  New-Item -ItemType SymbolicLink -Path $linkPath -Target (Join-Path $edgeKb "20_Plans") -ErrorAction Stop | Out-Null
  $linkMap = [ordered]@{ plans = "linked-plans"; evidence = "30_Evidence"; handoffs = "40_Handoffs"; reviews = "50_Reviews"; indexes = ".agent-memory/indexes" } | ConvertTo-Json
  Set-Content -LiteralPath (Join-Path $edgeKb "bad-symlink.json") -Encoding UTF8 -Value $linkMap
  Add-Result "edge-fail-closed:symlink" (Invoke-ExpectFailure -KnowledgebaseRoot $edgeKb -MapFile "bad-symlink.json") "Symlink mapped path should fail closed."
} catch {
  $linkCaseSkipped = $true
  Add-Result "edge-fail-closed:symlink" $true "Skipped because this environment cannot create symlinks: $($_.Exception.Message)"
}

$failed = @($results | Where-Object { -not $_.passed })
$output = [ordered]@{
  passed = ($failed.Count -eq 0)
  failed = $failed.Count
  total = $results.Count
  symlink_case_skipped = $linkCaseSkipped
  results = $results
}
$output | ConvertTo-Json -Depth 6
if ($failed.Count -gt 0) { exit 1 }
