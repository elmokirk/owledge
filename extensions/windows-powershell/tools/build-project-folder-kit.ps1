[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)]
  [string]$OutputPath,
  [string]$ProjectRoot = "",
  [switch]$Force,
  [switch]$IncludeGlobalMemory,
  [switch]$IncludePluginAdapter,
  [switch]$IncludeCompliance,
  [ValidateSet("auto", "windows", "unix")]
  [string]$PluginHookProfile = "auto",
  [switch]$Verify
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$scriptRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
  $ProjectRoot = (Resolve-Path (Join-Path $scriptRoot "..")).Path
}

function Copy-FileSafe {
  param([string]$Source, [string]$Destination)
  $parent = Split-Path -Parent $Destination
  if ($parent) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
  Copy-Item -LiteralPath $Source -Destination $Destination -Force
}

function Copy-TreeFiltered {
  param([string]$SourceRoot, [string]$DestinationRoot, [string[]]$ExcludeFragments = @())
  Get-ChildItem -LiteralPath $SourceRoot -Recurse -File | ForEach-Object {
    $relative = $_.FullName.Substring($SourceRoot.Length).TrimStart("\", "/")
    $normalized = $relative.Replace("\", "/")
    foreach ($fragment in $ExcludeFragments) {
      if ($normalized -like $fragment) { return }
    }
    Copy-FileSafe -Source $_.FullName -Destination (Join-Path $DestinationRoot $relative)
  }
}

$source = (Resolve-Path -LiteralPath $ProjectRoot).Path
$target = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutputPath)
if ((Test-Path -LiteralPath $target) -and -not $Force) {
  throw "OutputPath already exists. Pass -Force to replace: $target"
}
if (Test-Path -LiteralPath $target) {
  $resolved = (Resolve-Path -LiteralPath $target).Path
  $safeReplaceRoots = New-Object System.Collections.Generic.List[string]
  if (Test-Path -LiteralPath "C:\tmp") {
    $safeReplaceRoots.Add((Resolve-Path -LiteralPath "C:\tmp").Path)
  }
  $projectTmp = Join-Path $source ".agent-control\tmp"
  $safeReplaceRoots.Add($ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($projectTmp))
  $isSafeReplace = $false
  foreach ($safeRoot in $safeReplaceRoots) {
    if ($resolved.StartsWith($safeRoot, [StringComparison]::OrdinalIgnoreCase)) {
      $isSafeReplace = $true
    }
  }
  if (-not $isSafeReplace) {
    throw "Refusing to replace an existing folder outside C:\tmp or project .agent-control\tmp: $resolved"
  }
  Remove-Item -LiteralPath $target -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $target | Out-Null

$rootFiles = @(
  @{ Source = "PROJECT_CONTEXT.template.md"; Target = "PROJECT_CONTEXT.md" },
  @{ Source = "AGENTS.template.md"; Target = "AGENTS.md" },
  @{ Source = "CLAUDE.template.md"; Target = "CLAUDE.md" },
  @{ Source = "DESIGN.md"; Target = "DESIGN.md" },
  @{ Source = "REPORT_DESIGN_SELECTOR.html"; Target = "REPORT_DESIGN_SELECTOR.html" },
  @{ Source = ".gitignore"; Target = ".gitignore" }
)
foreach ($item in $rootFiles) {
  Copy-FileSafe -Source (Join-Path $source $item.Source) -Destination (Join-Path $target $item.Target)
}

$agentExclude = @(
  "exports/rag/*",
  "exports/lightrag/*",
  "exports/graphrag/*",
  "exports/retrieval-eval/*",
  "exports/compliance/*",
  "indexes/*.json*",
  "compliance/*",
  "templates/processing-activity-template.md",
  "templates/ai-system-template.md",
  "templates/provider-registry-template.md",
  "templates/dpia-trigger-template.md",
  "templates/data-subject-request-template.md",
  "templates/security-incident-template.md",
  "schemas/compliance-record.schema.json",
  "pi-agent/reports/*.md",
  "pi-agent/red-team/*.md",
  "pi-agent/evaluations/*.md",
  "pi-agent/scorecards/*.md",
  "tmp/*",
  "scratch/*",
  "sessions/*/events.jsonl",
  "sessions/*/session.md",
  "sessions/*/summary.md"
)
Copy-TreeFiltered -SourceRoot (Join-Path $source "agent-memory") -DestinationRoot (Join-Path $target "agent-memory") -ExcludeFragments $agentExclude
foreach ($dir in @(
  "canonical","compiled","patterns","lessons","ideas","decisions","evidence","evidence/promotions",
  "handoffs","indexes","exports/rag","exports/lightrag","exports/graphrag","sessions",
  "pi-agent/reports","pi-agent/parallels","pi-agent/trends","pi-agent/recurring-errors",
  "pi-agent/concepts","pi-agent/red-team","pi-agent/evaluations","pi-agent/scorecards","pi-agent/indexes"
)) {
  $dirPath = Join-Path $target "agent-memory/$dir"
  New-Item -ItemType Directory -Force -Path $dirPath | Out-Null
  New-Item -ItemType File -Force -Path (Join-Path $dirPath ".gitkeep") | Out-Null
}
if ($IncludeGlobalMemory) {
  Copy-TreeFiltered -SourceRoot (Join-Path $source "global-memory") -DestinationRoot (Join-Path $target "global-memory") -ExcludeFragments @("exports/*", "indexes/*.json*")
} else {
  foreach ($dir in @("preferences","goals","daily","tasks","ideas","research","patterns","coach","indexes","exports/rag","exports/lightrag","exports/graphrag")) {
    New-Item -ItemType Directory -Force -Path (Join-Path $target "global-memory/$dir") | Out-Null
    New-Item -ItemType File -Force -Path (Join-Path $target "global-memory/$dir/.gitkeep") | Out-Null
  }
}

$tools = @(
  "agent_memory_cli.py",
  "bootstrap-agent-memory.ps1",
  "build-context-pack.ps1",
  "build-context-pack.sh",
  "build-memory-index.ps1",
  "build-memory-index.sh",
  "build-project-folder-kit.ps1",
  "build-project-folder-kit.sh",
  "build_project_folder_kit.py",
  "build-kb-module.ps1",
  "build-kb-module.sh",
  "build_kb_module.py",
  "compact-sessions.ps1",
  "eval-memory-retrieval.ps1",
  "export-graphrag.ps1",
  "export-lightrag.ps1",
  "export-rag-documents.ps1",
  "find-parallels.ps1",
  "init-agent-memory.ps1",
  "memory-doctor.ps1",
  "memory-doctor.sh",
  "promote-memory.ps1",
  "render-memory-report.ps1",
  "report-agent-memory-metrics.ps1",
  "run-memory-evals.ps1",
  "run-review-workflow.ps1",
  "start-agent-control-plane.ps1",
  "test-agent-memory-principles-scenarios.ps1",
  "test-agent-memory-principles-skill.ps1",
  "test-kb-module.ps1",
  "validate-memory.ps1",
  "validate-memory.sh",
  "verify-host-install.ps1",
  "verify-host-install.sh",
  "audit-retention.ps1",
  "review-memory-conflicts.ps1",
  "scan-memory-sensitive-data.ps1"
)
foreach ($tool in $tools) {
  Copy-FileSafe -Source (Join-Path $source "tools/$tool") -Destination (Join-Path $target "tools/$tool")
}

Copy-TreeFiltered -SourceRoot (Join-Path $source "skills/agent-memory-principles") -DestinationRoot (Join-Path $target "skills/agent-memory-principles")
Copy-TreeFiltered -SourceRoot (Join-Path $source "skills/agent-memory-runtime-bridge") -DestinationRoot (Join-Path $target "skills/agent-memory-runtime-bridge")
Copy-TreeFiltered -SourceRoot (Join-Path $source "skills/review-evaluation-workflow") -DestinationRoot (Join-Path $target "skills/review-evaluation-workflow")
Copy-TreeFiltered -SourceRoot (Join-Path $source "skills/render-memory-report") -DestinationRoot (Join-Path $target "skills/render-memory-report")

if ($IncludePluginAdapter) {
  Copy-TreeFiltered -SourceRoot (Join-Path $source "plugins/agent-memory-cowork") -DestinationRoot (Join-Path $target "plugins/agent-memory-cowork") -ExcludeFragments @("tests/*")
  $effectiveHookProfile = $PluginHookProfile
  if ($effectiveHookProfile -eq "auto") {
    $effectiveHookProfile = if ([System.IO.Path]::DirectorySeparatorChar -eq "/") { "unix" } else { "windows" }
  }
  if ($effectiveHookProfile -eq "unix") {
    Copy-FileSafe -Source (Join-Path $target "plugins/agent-memory-cowork/hooks/hooks.unix.json") -Destination (Join-Path $target "plugins/agent-memory-cowork/hooks/hooks.json")
  }
} else {
  $effectiveHookProfile = "none"
}

if ($IncludeCompliance) {
  $complianceInstaller = Join-Path $source "addons\compliance-light\install-compliance-layer.ps1"
  if (-not (Test-Path -LiteralPath $complianceInstaller)) {
    throw "Compliance Light add-on is missing. Expected installer: $complianceInstaller"
  }
  & $complianceInstaller -ProjectRoot $target -Force | Out-Host
  if (-not $?) { exit 1 }
}

@"
# Agent Memory Project Folder Kit

This folder is a minimal project-local Agent Memory install.

1. Fill `PROJECT_CONTEXT.md`.
2. Verify:
   - Windows: `tools\verify-host-install.ps1 -ProjectRoot .`
   - macOS/Linux: `bash tools/verify-host-install.sh --project-root .`
3. Build the index:
   - Windows: `tools\build-memory-index.ps1 -ProjectRoot .`
   - macOS/Linux: `bash tools/build-memory-index.sh --project-root .`

Markdown is the source of truth. Generated indexes and exports are rebuildable views.

Agents should read `PROJECT_CONTEXT.md`, then use `agent-memory/` plus
`tools/agent_memory_cli.py` from this folder. No global `AGENT_MEMORY_KIT_ROOT`
variable is required after generation.

Compliance Light is not part of the default minimal kit. If this folder was
generated with `-IncludeCompliance`, run `tools\compliance-doctor.ps1 -ProjectRoot .`.
"@ | Set-Content -LiteralPath (Join-Path $target "README.md") -Encoding UTF8

$result = [ordered]@{
  output_path = $target
  include_global_memory = [bool]$IncludeGlobalMemory
  include_plugin_adapter = [bool]$IncludePluginAdapter
  plugin_hook_profile = $effectiveHookProfile
  include_compliance = [bool]$IncludeCompliance
  verified = $false
}
if ($Verify) {
  & (Join-Path $target "tools\verify-host-install.ps1") -ProjectRoot $target | Out-Host
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  if ($IncludeCompliance) {
    & (Join-Path $target "tools\compliance-doctor.ps1") -ProjectRoot $target | Out-Host
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  }
  $result.verified = $true
}
$result | ConvertTo-Json -Depth 5
