[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = (Resolve-Path -LiteralPath $ProjectRoot).Path
$gates = New-Object System.Collections.Generic.List[object]

function Resolve-Tool {
  param([string]$Name)
  $projectTool = Join-Path $root "tools\$Name"
  if (Test-Path -LiteralPath $projectTool) { return $projectTool }
  $addonTool = Join-Path $PSScriptRoot $Name
  if (Test-Path -LiteralPath $addonTool) { return $addonTool }
  throw "Missing required tool $Name. Install Compliance Light or the base Agent Memory Kit tools."
}

function Run-Gate {
  param([string]$Name, [scriptblock]$Command)
  $started = Get-Date
  $output = @()
  try {
    $global:LASTEXITCODE = 0
    $output = & $Command 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Exit code $LASTEXITCODE" }
    $gates.Add([ordered]@{ name = $Name; passed = $true; seconds = [math]::Round(((Get-Date) - $started).TotalSeconds, 3) })
  } catch {
    $preview = if ($output) { ($output | Select-Object -Last 8) -join [Environment]::NewLine } else { "" }
    $gates.Add([ordered]@{ name = $Name; passed = $false; error = $_.Exception.Message; output_preview = $preview; seconds = [math]::Round(((Get-Date) - $started).TotalSeconds, 3) })
  }
}

Run-Gate "validate" { & (Resolve-Tool "validate-memory.ps1") -ProjectRoot $root }
Run-Gate "retention" { & (Resolve-Tool "audit-retention.ps1") -ProjectRoot $root }
Run-Gate "conflicts" { & (Resolve-Tool "review-memory-conflicts.ps1") -ProjectRoot $root }
Run-Gate "sensitive-scan" { & (Resolve-Tool "scan-memory-sensitive-data.ps1") -ProjectRoot $root }
Run-Gate "compliance-doctor" { & (Resolve-Tool "compliance-doctor.ps1") -ProjectRoot $root }

$failed = @($gates | Where-Object { -not $_.passed })
$reportDir = Join-Path $root "agent-memory\exports\compliance"
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
$result = [ordered]@{
  generated_at = [DateTimeOffset]::UtcNow.ToString("o")
  project = $root
  passed = ($failed.Count -eq 0)
  gates = $gates
  failed = $failed.Count
  policy = "compliance-light-v0.1-read-only"
}
$json = $result | ConvertTo-Json -Depth 8
Set-Content -LiteralPath (Join-Path $reportDir "latest.json") -Value $json -Encoding UTF8
$summary = @(
  "# Compliance Light Gates"
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
