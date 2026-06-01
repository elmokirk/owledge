[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path,
  [string]$KitRoot = $env:AGENT_MEMORY_KIT_ROOT,
  [switch]$Force,
  [switch]$IncludeCompliance
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-RequiredPath {
  param(
    [string]$Path,
    [string]$Name
  )
  if ([string]::IsNullOrWhiteSpace($Path)) {
    throw "$Name is required. Set AGENT_MEMORY_KIT_ROOT or pass -KitRoot."
  }
  return (Resolve-Path -LiteralPath $Path).Path
}

function Copy-IfMissing {
  param(
    [string]$Source,
    [string]$Destination,
    [switch]$ForceCopy
  )
  if ((Test-Path -LiteralPath $Destination) -and -not $ForceCopy) {
    return "exists"
  }
  $parent = Split-Path -Parent $Destination
  if ($parent) {
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
  }
  Copy-Item -LiteralPath $Source -Destination $Destination -Force:$ForceCopy
  return "copied"
}

function Copy-DirectoryIfMissing {
  param(
    [string]$Source,
    [string]$Destination,
    [switch]$ForceCopy
  )
  New-Item -ItemType Directory -Force -Path $Destination | Out-Null
  $copied = 0
  $existing = 0
  $sourceFiles = Get-ChildItem -LiteralPath $Source -Recurse -File
  foreach ($sourceFile in $sourceFiles) {
    $relative = $sourceFile.FullName.Substring($Source.Length).TrimStart("\", "/")
    $target = Join-Path $Destination $relative
    if ((Test-Path -LiteralPath $target) -and -not $ForceCopy) {
      $existing += 1
      continue
    }
    $parent = Split-Path -Parent $target
    if ($parent) {
      New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }
    Copy-Item -LiteralPath $sourceFile.FullName -Destination $target -Force
    $copied += 1
  }
  if ($copied -gt 0 -and $existing -gt 0) { return "repaired:$copied copied,$existing existing" }
  if ($copied -gt 0) { return "copied:$copied" }
  return "exists:$existing"
}

$project = Resolve-RequiredPath -Path $ProjectRoot -Name "ProjectRoot"
$kit = Resolve-RequiredPath -Path $KitRoot -Name "KitRoot"
$python = if ($env:AGENT_MEMORY_PYTHON) { $env:AGENT_MEMORY_PYTHON } else { "python" }

$requiredKitFiles = @(
  "PROJECT_CONTEXT.template.md",
  "USER_CONTEXT.template.md",
  "AGENTS.template.md",
  "CLAUDE.template.md",
  "DESIGN.md",
  "REPORT_DESIGN_SELECTOR.html",
  "tools\agent_memory_cli.py"
)

foreach ($relative in $requiredKitFiles) {
  $path = Join-Path $kit $relative
  if (-not (Test-Path -LiteralPath $path)) {
    throw "KitRoot is missing required file: $relative"
  }
}

$results = [ordered]@{}
$results["USER_CONTEXT.md"] = Copy-IfMissing -Source (Join-Path $kit "USER_CONTEXT.template.md") -Destination (Join-Path $project "USER_CONTEXT.md") -ForceCopy:$Force
$results["PROJECT_CONTEXT.md"] = Copy-IfMissing -Source (Join-Path $kit "PROJECT_CONTEXT.template.md") -Destination (Join-Path $project "PROJECT_CONTEXT.md") -ForceCopy:$Force
$results["AGENTS.md"] = Copy-IfMissing -Source (Join-Path $kit "AGENTS.template.md") -Destination (Join-Path $project "AGENTS.md") -ForceCopy:$Force
$results["CLAUDE.md"] = Copy-IfMissing -Source (Join-Path $kit "CLAUDE.template.md") -Destination (Join-Path $project "CLAUDE.md") -ForceCopy:$Force
$results["DESIGN.md"] = Copy-IfMissing -Source (Join-Path $kit "DESIGN.md") -Destination (Join-Path $project "DESIGN.md") -ForceCopy:$Force
$results["REPORT_DESIGN_SELECTOR.html"] = Copy-IfMissing -Source (Join-Path $kit "REPORT_DESIGN_SELECTOR.html") -Destination (Join-Path $project "REPORT_DESIGN_SELECTOR.html") -ForceCopy:$Force
$results["agent-memory"] = Copy-DirectoryIfMissing -Source (Join-Path $kit "agent-memory") -Destination (Join-Path $project "agent-memory") -ForceCopy:$Force
$results["global-memory"] = Copy-DirectoryIfMissing -Source (Join-Path $kit "global-memory") -Destination (Join-Path $project "global-memory") -ForceCopy:$Force
$results["tools"] = Copy-DirectoryIfMissing -Source (Join-Path $kit "tools") -Destination (Join-Path $project "tools") -ForceCopy:$Force
if ($IncludeCompliance) {
  $complianceInstaller = Join-Path $kit "addons\compliance-light\install-compliance-layer.ps1"
  if (-not (Test-Path -LiteralPath $complianceInstaller)) {
    throw "Compliance Light add-on is missing. Expected installer: $complianceInstaller"
  }
  & $complianceInstaller -ProjectRoot $project -Force:$Force | Out-Host
  if (-not $?) { exit 1 }
  $results["compliance-light"] = "installed"
}

$gitignore = Join-Path $project ".gitignore"
$entries = @(
  "USER_CONTEXT.md",
  "global-memory/**/*.md",
  "global-memory/indexes/*.jsonl",
  "global-memory/exports/rag/*.json",
  "global-memory/exports/rag/*.jsonl",
  "global-memory/exports/rag/*/",
  "global-memory/exports/lightrag/*.json",
  "global-memory/exports/lightrag/*.jsonl",
  "global-memory/exports/lightrag/*/",
  "global-memory/exports/graphrag/*.json",
  "global-memory/exports/graphrag/*.jsonl",
  "global-memory/exports/graphrag/*/",
  "agent-plans/",
  "agent-memory/tmp/",
  "agent-memory/scratch/",
  "agent-memory/reports/html/",
  "agent-memory/sessions/**/events.jsonl",
  "agent-memory/sessions/**/session.md",
  "agent-memory/sessions/**/summary.md",
  "agent-memory/sessions/**/.session.lock"
)
if ($IncludeCompliance) {
  $entries += "agent-memory/exports/compliance/"
}
if (-not (Test-Path -LiteralPath $gitignore)) {
  New-Item -ItemType File -Path $gitignore | Out-Null
}
$existing = Get-Content -LiteralPath $gitignore -ErrorAction SilentlyContinue
foreach ($entry in $entries) {
  if ($existing -notcontains $entry) {
    Add-Content -LiteralPath $gitignore -Value $entry
  }
}

& $python (Join-Path $project "tools\agent_memory_cli.py") --project-root $project doctor --mode host | Out-Host
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

[pscustomobject]@{
  project_root = $project
  kit_root = $kit
  include_compliance = [bool]$IncludeCompliance
  results = $results
  next = "Fill PROJECT_CONTEXT.md placeholders, then run tools\validate-memory.ps1 -ProjectRoot ."
} | ConvertTo-Json -Depth 5
