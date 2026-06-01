[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path,
  [switch]$IncludeExports,
  [switch]$IncludeCompliance
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = (Resolve-Path -LiteralPath $ProjectRoot).Path
$gates = New-Object System.Collections.Generic.List[object]

function Test-WritableDirectory {
  param([string]$Path)
  try {
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
    $probe = Join-Path $Path (".agent-memory-write-probe-" + [Guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $probe | Out-Null
    Remove-Item -LiteralPath $probe -Recurse -Force
    return $true
  } catch {
    return $false
  }
}

$tmpBase = if (Test-WritableDirectory "C:\tmp") { "C:\tmp" } else { Join-Path $root ".agent-control\tmp" }
New-Item -ItemType Directory -Force -Path $tmpBase | Out-Null
$projectKitOutput = Join-Path $tmpBase "agent-memory-project-kit"
$projectKitComplianceOutput = Join-Path $tmpBase "agent-memory-project-kit-compliance"

function Run-Gate {
  param([string]$Name, [scriptblock]$Command)
  $started = Get-Date
  try {
    $global:LASTEXITCODE = 0
    & $Command | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "Exit code $LASTEXITCODE" }
    $gates.Add([ordered]@{ name = $Name; passed = $true; seconds = [math]::Round(((Get-Date) - $started).TotalSeconds, 3) })
  } catch {
    $gates.Add([ordered]@{ name = $Name; passed = $false; error = $_.Exception.Message; seconds = [math]::Round(((Get-Date) - $started).TotalSeconds, 3) })
  }
}

Run-Gate "python-compile" { python -m py_compile (Join-Path $root "tools\agent_memory_cli.py") }
Run-Gate "contracts" { & (Join-Path $root "tools\test-agent-memory-contracts.ps1") -ProjectRoot $root }
Run-Gate "doctor" { & (Join-Path $root "tools\memory-doctor.ps1") -ProjectRoot $root }
Run-Gate "validate" { & (Join-Path $root "tools\validate-memory.ps1") -ProjectRoot $root }
Run-Gate "index-full" { & (Join-Path $root "tools\build-memory-index.ps1") -ProjectRoot $root }
Run-Gate "index-incremental" { & (Join-Path $root "tools\build-memory-index.ps1") -ProjectRoot $root -Incremental -TrackTombstones }
Run-Gate "retention" { & (Join-Path $root "tools\audit-retention.ps1") -ProjectRoot $root }
Run-Gate "conflicts" { & (Join-Path $root "tools\review-memory-conflicts.ps1") -ProjectRoot $root }
Run-Gate "sensitive-scan" { & (Join-Path $root "tools\scan-memory-sensitive-data.ps1") -ProjectRoot $root }
Run-Gate "runtime-adapters" { & (Join-Path $root "tools\test-runtime-adapters.ps1") -ProjectRoot $root }
Run-Gate "memory-evals" { & (Join-Path $root "tools\run-memory-evals.ps1") -ProjectRoot $root }
Run-Gate "retrieval-fixture" { & (Join-Path $root "tools\eval-memory-retrieval.ps1") -ProjectRoot $root -ProjectRoots (Join-Path $root "tests\fixtures\retrieval-corpus") -QueriesFile (Join-Path $root "tests\fixtures\retrieval-queries.json") -MinOverallScore 85 -MinSafetyScore 100 }
Run-Gate "project-folder-kit" { & (Join-Path $root "tools\build-project-folder-kit.ps1") -ProjectRoot $root -OutputPath $projectKitOutput -Force -Verify }
if ($IncludeCompliance) {
  Run-Gate "compliance-addon-source" {
    $installer = Join-Path $root "addons\compliance-light\install-compliance-layer.ps1"
    $manifest = Join-Path $root "addons\compliance-light\addon.json"
    if (-not (Test-Path -LiteralPath $installer)) {
      throw "Compliance Light add-on is not installed in this kit. Expected $installer"
    }
    if (-not (Test-Path -LiteralPath $manifest)) {
      throw "Compliance Light manifest is missing. Expected $manifest"
    }
    Get-Content -LiteralPath $manifest -Raw | ConvertFrom-Json | Out-Null
  }
  Run-Gate "project-folder-kit-compliance" { & (Join-Path $root "tools\build-project-folder-kit.ps1") -ProjectRoot $root -OutputPath $projectKitComplianceOutput -Force -Verify -IncludeCompliance }
  Run-Gate "compliance-gates" { & (Join-Path $projectKitComplianceOutput "tools\run-compliance-gates.ps1") -ProjectRoot $projectKitComplianceOutput }
}
if ($IncludeExports) {
  Run-Gate "export-rag-shared" { & (Join-Path $root "tools\export-rag-documents.ps1") -ProjectRoot $root -CorpusType shared }
  Run-Gate "export-lightrag-shared" { & (Join-Path $root "tools\export-lightrag.ps1") -ProjectRoot $root -CorpusType shared }
  Run-Gate "export-graphrag-shared" { & (Join-Path $root "tools\export-graphrag.ps1") -ProjectRoot $root -CorpusType shared }
  Run-Gate "report-shared" { & (Join-Path $root "tools\render-memory-report.ps1") -ProjectRoot $root -ReportType project-dashboard -Audience shared }
}

$failed = @($gates | Where-Object { -not $_.passed })
$reportDir = Join-Path $root "agent-memory\exports\finalization-gates"
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
$result = [ordered]@{
  generated_at = [DateTimeOffset]::UtcNow.ToString("o")
  project = $root
  passed = ($failed.Count -eq 0)
  gates = $gates
  failed = $failed.Count
  include_compliance = [bool]$IncludeCompliance
}
$json = $result | ConvertTo-Json -Depth 8
Set-Content -LiteralPath (Join-Path $reportDir "latest.json") -Value $json -Encoding UTF8
$summary = @(
  "# Finalization Gates"
  ""
  "- Generated at: $($result.generated_at)"
  "- Passed: $($result.passed)"
  "- Failed gates: $($result.failed)"
  ""
  "## Gates"
  ""
)
foreach ($gate in $gates) {
  $status = if ($gate.passed) { "PASS" } else { "FAIL" }
  $line = "- $status `$($gate.name)` in $($gate.seconds)s"
  if (-not $gate.passed -and $gate.error) { $line += " - $($gate.error)" }
  $summary += $line
}
Set-Content -LiteralPath (Join-Path $reportDir "latest.md") -Value ($summary -join [Environment]::NewLine) -Encoding UTF8
$json
if ($failed.Count -gt 0) { exit 1 }
