[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = (Resolve-Path -LiteralPath $ProjectRoot).Path
$fixtures = Join-Path $root "plugins\agent-memory-cowork\tests\fixtures"
if (-not (Test-Path -LiteralPath $fixtures)) { throw "Missing plugin fixtures: $fixtures" }

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
$tmpRoot = Join-Path $tmpBase ("agent-memory-runtime-smoke-" + [Guid]::NewGuid().ToString("N"))

$previousCaptureMode = $env:AGENT_MEMORY_CAPTURE_MODE
$python = if ($env:AGENT_MEMORY_PYTHON) { $env:AGENT_MEMORY_PYTHON } else { "python" }
try {
  & (Join-Path $root "tools\build-project-folder-kit.ps1") -ProjectRoot $root -OutputPath $tmpRoot -Force -IncludePluginAdapter | Out-Null
  $env:AGENT_MEMORY_CAPTURE_MODE = "standard"

  $capture = Join-Path $root "plugins\agent-memory-cowork\scripts\capture-claude-event.ps1"
  $close = Join-Path $root "plugins\agent-memory-cowork\scripts\close-runtime-session.ps1"

  Push-Location $tmpRoot
  try {
    foreach ($fixture in @("session-start.json", "user-prompt.json", "post-tool-use.json")) {
      Get-Content -LiteralPath (Join-Path $fixtures $fixture) -Raw | & $capture | Out-Null
    }
    Get-Content -LiteralPath (Join-Path $fixtures "stop.json") -Raw | & $close | Out-Null
  } finally {
    Pop-Location
  }

  $sessionDir = Join-Path $tmpRoot "agent-memory\sessions\cowork-demo-session"
  $required = @("events.jsonl", "session.md", "summary.md")
  $missing = @()
  foreach ($file in $required) {
    if (-not (Test-Path -LiteralPath (Join-Path $sessionDir $file))) { $missing += $file }
  }
  if ($missing.Count -gt 0) { throw "Runtime smoke missing files: $($missing -join ', ')" }

  $summary = Get-Content -LiteralPath (Join-Path $sessionDir "summary.md") -Raw
  if ($summary -notmatch 'visibility: "private"' -and $summary -notmatch "visibility: private") { throw "Runtime summary is not private." }

  $capturePy = Join-Path $tmpRoot "plugins\agent-memory-cowork\scripts\capture-claude-event.py"
  $closePy = Join-Path $tmpRoot "plugins\agent-memory-cowork\scripts\close-runtime-session.py"
  Push-Location $tmpRoot
  try {
    foreach ($fixture in @("session-start.json", "user-prompt.json")) {
      Get-Content -LiteralPath (Join-Path $fixtures $fixture) -Raw | & $python $capturePy | Out-Null
      if ($LASTEXITCODE -ne 0) { throw "Python Unix capture hook failed for $fixture" }
    }
    Get-Content -LiteralPath (Join-Path $fixtures "stop.json") -Raw | & $python $closePy | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Python Unix close hook failed" }
  } finally {
    Pop-Location
  }

  @{
    passed = $true
    temp_project = $tmpRoot
    session_dir = $sessionDir
    checked_files = $required
    checked_unix_python_hooks = $true
  } | ConvertTo-Json -Depth 5
} finally {
  $env:AGENT_MEMORY_CAPTURE_MODE = $previousCaptureMode
}
