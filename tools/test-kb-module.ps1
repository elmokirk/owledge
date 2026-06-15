[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = (Resolve-Path -LiteralPath $ProjectRoot).Path
$tmpBase = Join-Path $root ".agent-control\tmp"
New-Item -ItemType Directory -Force -Path $tmpBase | Out-Null
$kb = Join-Path $tmpBase "kb-module-smoke"
if (Test-Path -LiteralPath $kb) {
  Remove-Item -LiteralPath $kb -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $kb | Out-Null

$noteA = Join-Path $kb "Project Alpha.md"
$noteB = Join-Path $kb "Research.md"
Set-Content -LiteralPath $noteA -Encoding UTF8 -Value @"
# Project Alpha

Links to [[Research]] and keeps the original wiki link untouched.
"@
Set-Content -LiteralPath $noteB -Encoding UTF8 -Value @"
---
type: research
status: active
---

# Research

Source note.
"@

$hashBeforeA = (Get-FileHash -Algorithm SHA256 -LiteralPath $noteA).Hash
$hashBeforeB = (Get-FileHash -Algorithm SHA256 -LiteralPath $noteB).Hash

$builder = Join-Path $root "tools\build-kb-module.ps1"
& $builder -KnowledgebaseRoot $kb -KitRoot $root -IncludeCli | Out-Host
if ($LASTEXITCODE -ne 0) { throw "build-kb-module failed with exit code $LASTEXITCODE" }

$hashAfterA = (Get-FileHash -Algorithm SHA256 -LiteralPath $noteA).Hash
$hashAfterB = (Get-FileHash -Algorithm SHA256 -LiteralPath $noteB).Hash
if ($hashBeforeA -ne $hashAfterA -or $hashBeforeB -ne $hashAfterB) {
  throw "Existing KB markdown files were modified."
}

$moduleRoot = Join-Path $kb "agent-memory-module"
$required = @(
  "AGENT_MEMORY_MODULE.md",
  "agent-memory\plans\example-kb-backed-project-plan.md",
  "agent-memory\indexes\kb-scan.jsonl",
  "agent-memory\indexes\kb-module-status.json",
  "tools\agent_memory_cli.py"
)
foreach ($relative in $required) {
  $path = Join-Path $moduleRoot $relative
  if (-not (Test-Path -LiteralPath $path)) {
    throw "Missing expected module file: $path"
  }
}

$scanText = Get-Content -LiteralPath (Join-Path $moduleRoot "agent-memory\indexes\kb-scan.jsonl") -Raw
if ($scanText -notmatch "\[\[Research\]\]" -and $scanText -notmatch '"Research"') {
  throw "Wiki link metadata was not captured in the generated index."
}

$status = Get-Content -LiteralPath (Join-Path $moduleRoot "agent-memory\indexes\kb-module-status.json") -Raw | ConvertFrom-Json
if ($status.markdown_files_scanned -lt 2) {
  throw "Expected at least two Markdown files to be scanned."
}
if ($status.existing_kb_files_modified -ne $false) {
  throw "Status did not report existing_kb_files_modified=false."
}
if ($status.requires_os_environment_variables -ne $false) {
  throw "Status did not report requires_os_environment_variables=false."
}

$mappedKb = Join-Path $tmpBase "kb-module-mapped-smoke"
if (Test-Path -LiteralPath $mappedKb) {
  Remove-Item -LiteralPath $mappedKb -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $mappedKb | Out-Null
Set-Content -LiteralPath (Join-Path $mappedKb "Idea.md") -Encoding UTF8 -Value "# Idea`n`nTurn [[Research]] into an MVP."
Set-Content -LiteralPath (Join-Path $mappedKb "Research.md") -Encoding UTF8 -Value "# Research`n`nSource note."
foreach ($relative in @("01_Ideas","20_Plans","30_Evidence","40_Handoffs","50_Reviews",".agent-memory\indexes")) {
  New-Item -ItemType Directory -Force -Path (Join-Path $mappedKb $relative) | Out-Null
}
$map = [ordered]@{
  ideas = "01_Ideas"
  plans = "20_Plans"
  evidence = "30_Evidence"
  handoffs = "40_Handoffs"
  reviews = "50_Reviews"
  indexes = ".agent-memory/indexes"
} | ConvertTo-Json
Set-Content -LiteralPath (Join-Path $mappedKb "agent-memory-map.json") -Encoding UTF8 -Value $map
& $builder -KnowledgebaseRoot $mappedKb -KitRoot $root -MapFile "agent-memory-map.json" | Out-Host
if ($LASTEXITCODE -ne 0) { throw "Mapped build-kb-module failed with exit code $LASTEXITCODE" }
if (-not (Test-Path -LiteralPath (Join-Path $mappedKb "20_Plans\example-kb-backed-project-plan.md"))) {
  throw "Mapped mode did not write the sample plan to the mapped plans folder."
}
if (-not (Test-Path -LiteralPath (Join-Path $mappedKb ".agent-memory\indexes\kb-scan.jsonl"))) {
  throw "Mapped mode did not write the index to the mapped indexes folder."
}
if (Test-Path -LiteralPath (Join-Path $mappedKb "AGENT_MEMORY_MODULE.md")) {
  throw "Mapped mode should not write AGENT_MEMORY_MODULE.md at the KB root."
}
if (-not (Test-Path -LiteralPath (Join-Path $mappedKb ".agent-memory\indexes\AGENT_MEMORY_MODULE.md"))) {
  throw "Mapped mode did not write AGENT_MEMORY_MODULE.md to the mapped indexes folder."
}
$mappedStatus = Get-Content -LiteralPath (Join-Path $mappedKb ".agent-memory\indexes\kb-module-status.json") -Raw | ConvertFrom-Json
if ($mappedStatus.mode -ne "mapped" -or $mappedStatus.mapping_enabled -ne $true) {
  throw "Mapped status did not report mode=mapped and mapping_enabled=true."
}

$badMap = [ordered]@{
  plans = "../escape"
  evidence = "30_Evidence"
  handoffs = "40_Handoffs"
  reviews = "50_Reviews"
  indexes = ".agent-memory/indexes"
} | ConvertTo-Json
Set-Content -LiteralPath (Join-Path $mappedKb "bad-agent-memory-map.json") -Encoding UTF8 -Value $badMap
$previousErrorActionPreference = $ErrorActionPreference
$previousNativeCommandPreference = $null
if (Test-Path -LiteralPath Variable:\PSNativeCommandUseErrorActionPreference) {
  $previousNativeCommandPreference = $PSNativeCommandUseErrorActionPreference
  $PSNativeCommandUseErrorActionPreference = $false
}
$ErrorActionPreference = "Continue"
$python = if ($env:AGENT_MEMORY_PYTHON) { $env:AGENT_MEMORY_PYTHON } else { "python" }
$builderPy = Join-Path $root "tools\build_kb_module.py"
& $python $builderPy --knowledgebase-root $mappedKb --kit-root $root --map-file "bad-agent-memory-map.json" 2>$null | Out-Null
$badMapExitCode = $LASTEXITCODE
$ErrorActionPreference = $previousErrorActionPreference
if ($null -ne $previousNativeCommandPreference) {
  $PSNativeCommandUseErrorActionPreference = $previousNativeCommandPreference
}
if ($badMapExitCode -eq 0) {
  throw "Invalid map with traversal path should fail closed."
}
$global:LASTEXITCODE = 0

[ordered]@{
  passed = $true
  knowledgebase = $kb
  module_root = $moduleRoot
  existing_files_unchanged = $true
  mapped_mode = $true
  invalid_map_failed_closed = $true
} | ConvertTo-Json -Depth 4
