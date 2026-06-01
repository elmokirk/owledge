[CmdletBinding()]
param(
  [string]$ProjectRoot = $env:AGENT_MEMORY_PROJECT_ROOT,
  [Parameter(ValueFromPipeline=$true)]
  [string]$PipedPayload = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-AgentMemoryPluginError {
  param([string]$Message, [string]$Root = "")
  try {
    $logRoot = if ($Root -and (Test-Path -LiteralPath $Root)) { Join-Path $Root ".agent-control\logs" } else { Join-Path $env:TEMP "agent-memory-plugin-logs" }
    New-Item -ItemType Directory -Force -Path $logRoot | Out-Null
    $row = [ordered]@{
      captured_at = [DateTimeOffset]::UtcNow.ToString("o")
      hook = "close-runtime-session"
      message = $Message
    } | ConvertTo-Json -Compress
    Add-Content -LiteralPath (Join-Path $logRoot "plugin-errors.jsonl") -Value $row -Encoding UTF8
  } catch {
  }
}

function Find-AgentMemoryRoot {
  param([string]$Start)
  if ($ProjectRoot) {
    $resolved = (Resolve-Path -LiteralPath $ProjectRoot).Path
    if (-not (Test-Path -LiteralPath (Join-Path $resolved "agent-memory"))) { throw "AGENT_MEMORY_PROJECT_ROOT does not contain agent-memory: $resolved" }
    if (-not (Test-Path -LiteralPath (Join-Path $resolved "PROJECT_CONTEXT.md")) -and -not $env:AGENT_MEMORY_PROJECT_ROOT_ALLOW_UNINITIALIZED) { throw "AGENT_MEMORY_PROJECT_ROOT is not initialized. Missing PROJECT_CONTEXT.md: $resolved" }
    return $resolved
  }
  $current = (Resolve-Path -LiteralPath $Start).Path
  while ($true) {
    if ((Test-Path -LiteralPath (Join-Path $current "PROJECT_CONTEXT.md")) -and (Test-Path -LiteralPath (Join-Path $current "agent-memory"))) { return $current }
    $parent = Split-Path -Parent $current
    if (-not $parent -or $parent -eq $current) { throw "Could not find Agent Memory project root. Set AGENT_MEMORY_PROJECT_ROOT." }
    $current = $parent
  }
}

function Resolve-AgentMemoryCli {
  param([string]$Root)
  $local = Join-Path $Root "tools\agent_memory_cli.py"
  if (Test-Path -LiteralPath $local) { return $local }
  if ($env:AGENT_MEMORY_KIT_ROOT) {
    $kitCli = Join-Path $env:AGENT_MEMORY_KIT_ROOT "tools\agent_memory_cli.py"
    if (Test-Path -LiteralPath $kitCli) { return $kitCli }
  }
  $pluginRoot = Split-Path -Parent $PSScriptRoot
  $repoCandidate = Split-Path -Parent (Split-Path -Parent $pluginRoot)
  $repoCli = Join-Path $repoCandidate "tools\agent_memory_cli.py"
  if (Test-Path -LiteralPath $repoCli) { return $repoCli }
  throw "Missing Agent Memory CLI. Set AGENT_MEMORY_KIT_ROOT or copy tools\agent_memory_cli.py into the project."
}

function Get-SessionIdFromPayload {
  param([string]$Payload)
  $event = $Payload | ConvertFrom-Json
  if ($event.session_id) { return [string]$event.session_id }
  if ($event.transcript_path) { return [System.IO.Path]::GetFileNameWithoutExtension([string]$event.transcript_path) }
  throw "Close hook payload must include session_id or transcript_path."
}

$root = ""
try {
  $root = Find-AgentMemoryRoot -Start (Get-Location).Path
  $cli = Resolve-AgentMemoryCli -Root $root
  $python = if ($env:AGENT_MEMORY_PYTHON) { $env:AGENT_MEMORY_PYTHON } else { "python" }
  $captureMode = if ($env:AGENT_MEMORY_CAPTURE_MODE) { $env:AGENT_MEMORY_CAPTURE_MODE } else { "standard" }
  $payload = if (-not [string]::IsNullOrWhiteSpace($PipedPayload)) { $PipedPayload } else { [Console]::In.ReadToEnd() }
  if ([string]::IsNullOrWhiteSpace($payload)) { $payload = "{}" }
  $sessionId = Get-SessionIdFromPayload -Payload $payload
  $tmp = [System.IO.Path]::GetTempFileName()
  try {
    [System.IO.File]::WriteAllText($tmp, $payload, [System.Text.UTF8Encoding]::new($false))
    & $python $cli --project-root $root capture-runtime-event --runtime claude-cowork --capture-mode $captureMode --event-file $tmp | Out-Null
    & $python $cli --project-root $root close-runtime-session --runtime claude-cowork --session-id $sessionId | Out-Null
  } finally {
    if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp -Force }
  }
} catch {
  Write-AgentMemoryPluginError -Root $root -Message $_.Exception.Message
  if ($env:AGENT_MEMORY_STRICT_HOOKS -eq "1") { exit 1 }
}
exit 0
