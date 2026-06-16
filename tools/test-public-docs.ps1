[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = (Resolve-Path -LiteralPath $ProjectRoot).Path
$results = New-Object System.Collections.Generic.List[object]

function Add-Result {
  param([string]$Name, [bool]$Passed, [string]$Details)
  $results.Add([ordered]@{
    name = $Name
    passed = $Passed
    details = $Details
  })
}

function Get-GitHubAnchor {
  param([string]$Heading)
  $text = $Heading.Trim().ToLowerInvariant()
  $text = [regex]::Replace($text, "[^\p{L}\p{Nd}\- ]", "")
  return ($text -replace " ", "-")
}

$publicFiles = @(
  "README.md",
  "docs\README.md",
  "docs\quickstart.md",
  "docs\agent-integration-guide.md",
  "docs\install-plugin.md",
  "docs\harness-plugin-matrix.md",
  "docs\mvp-plan-example.md",
  "docs\performance-scale-notes.md",
  "docs\team-long-running-project-guide.md",
  "docs\command-reference.md",
  "docs\owledge-vs-agent-methods.md",
  "plugins\agent-memory-cowork\README.md"
)

foreach ($relative in $publicFiles) {
  $path = Join-Path $root $relative
  Add-Result "exists:$relative" (Test-Path -LiteralPath $path) "Public doc exists."
}

$mojibakePatterns = @(
  [string][char]0x00C2,
  [string][char]0x00E2,
  [string][char]0x00EF
)
foreach ($relative in $publicFiles) {
  $path = Join-Path $root $relative
  if (-not (Test-Path -LiteralPath $path)) { continue }
  $content = Get-Content -LiteralPath $path -Raw
  $found = @($mojibakePatterns | Where-Object { $content.Contains($_) })
  Add-Result "utf8-clean:$relative" ($found.Count -eq 0) ($(if ($found.Count -eq 0) { "No mojibake patterns detected." } else { "Found: $($found -join ', ')" }))
}

$readmePath = Join-Path $root "README.md"
$readme = Get-Content -LiteralPath $readmePath -Raw
$headings = [regex]::Matches($readme, '(?m)^##+\s+(.+)$') | ForEach-Object { Get-GitHubAnchor $_.Groups[1].Value }
$tocLinks = [regex]::Matches($readme, '(?m)^\-\s+\[[^\]]+\]\(#([^)]+)\)') | ForEach-Object { $_.Groups[1].Value }
foreach ($anchor in $tocLinks) {
  Add-Result "toc-anchor:$anchor" ($headings -contains $anchor) "README table-of-contents anchor resolves to a heading."
}

foreach ($relative in $publicFiles) {
  $path = Join-Path $root $relative
  if (-not (Test-Path -LiteralPath $path)) { continue }
  $content = Get-Content -LiteralPath $path -Raw
  $fileDir = Split-Path -Parent $path
  $matches = [regex]::Matches($content, '\[[^\]]+\]\(([^)]+)\)')
  foreach ($match in $matches) {
    $target = $match.Groups[1].Value.Trim()
    if ($target.StartsWith("http://") -or $target.StartsWith("https://") -or $target.StartsWith("mailto:") -or $target.StartsWith("#")) { continue }
    $clean = $target.Split("#")[0]
    if ([string]::IsNullOrWhiteSpace($clean)) { continue }
    $resolved = [System.IO.Path]::GetFullPath((Join-Path $fileDir $clean))
    $name = "link:$relative->$clean"
    Add-Result $name (Test-Path -LiteralPath $resolved) "Relative markdown link resolves."
  }
}

$pluginDocs = @(
  (Join-Path $root "README.md"),
  (Join-Path $root "docs\install-plugin.md"),
  (Join-Path $root "docs\harness-plugin-matrix.md"),
  (Join-Path $root "plugins\agent-memory-cowork\README.md")
)
foreach ($path in $pluginDocs) {
  $content = Get-Content -LiteralPath $path -Raw
  $label = $path.Substring($root.Length + 1)
  Add-Result "plugin-path:$label" ($content -match 'plugins/agent-memory-cowork/' -or $content -match 'plugins\\agent-memory-cowork\\') "Public plugin doc references the canonical plugin path."
  Add-Result "no-projectroot-env:$label" (-not ($content -match 'AGENT_MEMORY_PROJECT_ROOT')) "Public plugin doc does not require AGENT_MEMORY_PROJECT_ROOT."
  Add-Result "no-kitroot-env:$label" (-not ($content -match 'AGENT_MEMORY_KIT_ROOT')) "Public plugin doc does not require AGENT_MEMORY_KIT_ROOT."
}

$docsIndex = Get-Content -LiteralPath (Join-Path $root "docs\README.md") -Raw
$requiredIndexLinks = @(
  "quickstart.md",
  "agent-integration-guide.md",
  "install-plugin.md",
  "harness-plugin-matrix.md",
  "mvp-plan-example.md",
  "performance-scale-notes.md",
  "team-long-running-project-guide.md",
  "command-reference.md"
)
foreach ($link in $requiredIndexLinks) {
  Add-Result "docs-index:$link" ($docsIndex -match [regex]::Escape($link)) "Docs index links the public entrypoint."
}

$benchmarkMention = ($readme -match 'benchmark') -or ((Get-Content -LiteralPath (Join-Path $root "docs\performance-scale-notes.md") -Raw) -match 'benchmark')
if ($benchmarkMention) {
  Add-Result "benchmark-assets:readme" (Test-Path -LiteralPath (Join-Path $root "benchmarks\README.md")) "Benchmark README exists."
  Add-Result "benchmark-assets:script" (Test-Path -LiteralPath (Join-Path $root "benchmarks\run-benchmarks.ps1")) "Benchmark runner exists."
}

$failed = @($results | Where-Object { -not $_.passed })
$output = [ordered]@{
  project = $root
  passed = ($failed.Count -eq 0)
  failed = $failed.Count
  total = $results.Count
  results = $results
}
$json = $output | ConvertTo-Json -Depth 6
$json
if ($failed.Count -gt 0) { exit 1 }
