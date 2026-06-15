[CmdletBinding()]
param(
  [string]$ProjectRoot = (Get-Location).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = (Resolve-Path -LiteralPath $ProjectRoot).Path
$skillRelative = "skills\agent-memory-principles"
$pluginRelative = "plugins\agent-memory-cowork\skills\agent-memory-principles"
$requiredReferences = @(
  "references\principles.md",
  "references\agent-rules.md",
  "references\mapping-contract.md",
  "references\security-rules.md"
)
$results = New-Object System.Collections.Generic.List[object]

function Add-Result {
  param([string]$Name, [bool]$Passed, [string]$Details)
  $results.Add([ordered]@{ name = $Name; passed = $Passed; details = $Details })
}

function Read-Frontmatter {
  param([string]$Path)
  $lines = Get-Content -LiteralPath $Path
  if ($lines.Count -lt 3 -or $lines[0].Trim() -ne "---") {
    throw "Missing YAML frontmatter in $Path"
  }
  $closingIndex = -1
  for ($i = 1; $i -lt $lines.Count; $i++) {
    if ($lines[$i].Trim() -eq "---") {
      $closingIndex = $i
      break
    }
  }
  if ($closingIndex -lt 2) {
    throw "Missing closing YAML frontmatter marker in $Path"
  }
  $frontmatter = @{}
  foreach ($line in $lines[1..($closingIndex - 1)]) {
    if ($line -match "^([A-Za-z0-9_-]+):\s*(.*)$") {
      $frontmatter[$Matches[1]] = $Matches[2].Trim().Trim('"')
    }
  }
  return [ordered]@{
    fields = $frontmatter
    line_count = $lines.Count
    body = ($lines[($closingIndex + 1)..($lines.Count - 1)] -join "`n")
  }
}

function Test-Skill {
  param([string]$RelativePath)
  $skillDir = Join-Path $root $RelativePath
  $skillPath = Join-Path $skillDir "SKILL.md"
  Add-Result "exists:$RelativePath" (Test-Path -LiteralPath $skillPath) "SKILL.md exists."
  if (-not (Test-Path -LiteralPath $skillPath)) { return }

  $parsed = Read-Frontmatter -Path $skillPath
  $name = if ($parsed.fields.ContainsKey("name")) { $parsed.fields["name"] } else { "" }
  $description = if ($parsed.fields.ContainsKey("description")) { $parsed.fields["description"] } else { "" }
  Add-Result "frontmatter-name:$RelativePath" ($name -eq "agent-memory-principles") "Expected name agent-memory-principles."
  Add-Result "frontmatter-description:$RelativePath" (-not [string]::IsNullOrWhiteSpace($description)) "Description is present."
  Add-Result "concise-skill:$RelativePath" ($parsed.line_count -le 90) "SKILL.md has $($parsed.line_count) lines; limit is 90."

  foreach ($reference in $requiredReferences) {
    $referencePath = Join-Path $skillDir $reference
    $linked = $parsed.body.Contains($reference.Replace("\", "/"))
    Add-Result "reference-linked:$RelativePath/$reference" $linked "Reference is linked from SKILL.md."
    Add-Result "reference-exists:$RelativePath/$reference" (Test-Path -LiteralPath $referencePath) "Reference file exists."
  }
}

Test-Skill -RelativePath $skillRelative
Test-Skill -RelativePath $pluginRelative

foreach ($reference in @("SKILL.md") + $requiredReferences) {
  $source = Join-Path (Join-Path $root $skillRelative) $reference
  $mirror = Join-Path (Join-Path $root $pluginRelative) $reference
  if ((Test-Path -LiteralPath $source) -and (Test-Path -LiteralPath $mirror)) {
    $sourceHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $source).Hash
    $mirrorHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $mirror).Hash
    Add-Result "mirror-identical:$reference" ($sourceHash -eq $mirrorHash) "Plugin mirror matches root skill file."
  }
}

$failed = @($results | Where-Object { -not $_.passed })
$output = [ordered]@{
  passed = ($failed.Count -eq 0)
  failed = $failed.Count
  total = $results.Count
  results = $results
}
$output | ConvertTo-Json -Depth 5
if ($failed.Count -gt 0) { exit 1 }
