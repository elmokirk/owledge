[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = (Resolve-Path -LiteralPath $ProjectRoot).Path
$resultsDir = Join-Path $root "benchmarks\results"
New-Item -ItemType Directory -Force -Path $resultsDir | Out-Null

function Measure-Step {
  param([string]$Name, [scriptblock]$Action)
  $started = Get-Date
  $value = & $Action
  [pscustomobject]@{
    name = $Name
    seconds = [math]::Round(((Get-Date) - $started).TotalSeconds, 3)
    data = $value
  }
}

function New-SyntheticVault {
  param([string]$Path, [int]$Count)
  New-Item -ItemType Directory -Force -Path $Path | Out-Null
  for ($i = 1; $i -le $Count; $i++) {
    $next = if ($i -lt $Count) { "[[note-$($i + 1)]]" } else { "[[note-1]]" }
    $body = @(
      "# Note $i"
      ""
      "This is a benchmark note."
      ""
      "- link: $next"
      "- tag: benchmark"
    ) -join [Environment]::NewLine
    Set-Content -LiteralPath (Join-Path $Path ("note-$i.md")) -Value $body -Encoding UTF8
  }
}

$tmpBase = Join-Path $root ".agent-control\tmp"
New-Item -ItemType Directory -Force -Path $tmpBase | Out-Null
$tmpRoot = Join-Path $tmpBase ("owledge-benchmarks-" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $tmpRoot | Out-Null

try {
  $vaultRoot = Join-Path $tmpRoot "vault"
  New-SyntheticVault -Path $vaultRoot -Count 100

  $kbStep = Measure-Step "kb-scan" {
    $output = python (Join-Path $root "tools\build_kb_module.py") --knowledgebase-root $vaultRoot --include-cli --max-files 1000
    $json = ($output -join "`n") | ConvertFrom-Json
    [pscustomobject]@{
      markdown_files_scanned = $json.markdown_files_scanned
      existing_files_modified = $json.existing_kb_files_modified
      index_path = $json.index_path
      module_root = $json.module_root
    }
  }

  $contextStep = Measure-Step "context-pack" {
    $output = powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root "tools\build-context-pack.ps1") -TaskId "benchmark-release" -ProjectRoot $root -AgentRole worker -Objective "Measure scoped context behavior" -BudgetChars 2400
    $json = ($output -join "`n") | ConvertFrom-Json
    [pscustomobject]@{
      estimated_tokens = $json.estimated_tokens
      included_sources = @($json.included_sources).Count
      dropped_sources = $json.dropped_sources
      output_bytes = [Text.Encoding]::UTF8.GetByteCount([string]$json.content)
      raw_chars_available = $json.raw_chars_available
    }
  }

  $runtimeStep = Measure-Step "runtime-handoff" {
    $output = powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root "tools\test-runtime-adapters.ps1") -ProjectRoot $root
    $json = ($output -join "`n") | ConvertFrom-Json
    $summaryPath = Join-Path $json.session_dir "summary.md"
    [pscustomobject]@{
      passed = $json.passed
      checked_files = @($json.checked_files).Count
      summary_bytes = if (Test-Path -LiteralPath $summaryPath) { (Get-Item -LiteralPath $summaryPath).Length } else { 0 }
    }
  }

  $report = [ordered]@{
    generated_at = [DateTimeOffset]::UtcNow.ToString("o")
    project = $root
    scenarios = @($kbStep, $contextStep, $runtimeStep)
  }
  $jsonText = $report | ConvertTo-Json -Depth 8
  Set-Content -LiteralPath (Join-Path $resultsDir "latest.json") -Value $jsonText -Encoding UTF8

  $lines = @(
    "# Benchmark Results",
    "",
    "- Generated at: $($report.generated_at)",
    "",
    "## Scenarios",
    ""
  )
  foreach ($scenario in $report.scenarios) {
    $lines += "- $($scenario.name): $($scenario.seconds)s"
  }
  Set-Content -LiteralPath (Join-Path $resultsDir "latest.md") -Value ($lines -join [Environment]::NewLine) -Encoding UTF8
  $jsonText
} finally {
  if (Test-Path -LiteralPath $tmpRoot) {
    Remove-Item -LiteralPath $tmpRoot -Recurse -Force
  }
}
