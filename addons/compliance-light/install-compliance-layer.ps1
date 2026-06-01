[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path,
  [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$addonRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$project = (Resolve-Path -LiteralPath $ProjectRoot).Path
$manifestPath = Join-Path $addonRoot "addon.json"
if (-not (Test-Path -LiteralPath $manifestPath)) {
  throw "Missing Compliance Light manifest: $manifestPath"
}
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json

function Copy-AddonFile {
  param([string]$Source, [string]$Destination)
  $parent = Split-Path -Parent $Destination
  if ($parent) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
  if ((Test-Path -LiteralPath $Destination) -and -not $Force) {
    return @{ path = $Destination; status = "skipped_exists" }
  }
  Copy-Item -LiteralPath $Source -Destination $Destination -Force
  return @{ path = $Destination; status = "copied" }
}

$results = New-Object System.Collections.Generic.List[object]
foreach ($dir in $manifest.install_directories) {
  $dirPath = Join-Path $project $dir
  New-Item -ItemType Directory -Force -Path $dirPath | Out-Null
  New-Item -ItemType File -Force -Path (Join-Path $dirPath ".gitkeep") | Out-Null
}

foreach ($file in $manifest.install_files) {
  $results.Add((Copy-AddonFile -Source (Join-Path $addonRoot $file.source) -Destination (Join-Path $project $file.target)))
}

$gitignore = Join-Path $project ".gitignore"
if (-not (Test-Path -LiteralPath $gitignore)) {
  New-Item -ItemType File -Path $gitignore | Out-Null
}
$text = Get-Content -LiteralPath $gitignore -Raw -ErrorAction SilentlyContinue
if ([string]::IsNullOrEmpty($text) -or $text -notmatch "(?m)^agent-memory/exports/compliance/$") {
  Add-Content -LiteralPath $gitignore -Value "agent-memory/exports/compliance/"
}

[ordered]@{
  installed = $true
  addon = $manifest.name
  addon_version = $manifest.version
  project = $project
  force = [bool]$Force
  files = $results
  next_commands = @(
    "tools\compliance-doctor.ps1 -ProjectRoot .",
    "tools\run-compliance-gates.ps1 -ProjectRoot ."
  )
} | ConvertTo-Json -Depth 6
