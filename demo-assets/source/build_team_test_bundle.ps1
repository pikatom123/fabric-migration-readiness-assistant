$ErrorActionPreference = "Stop"

$source = Split-Path -Parent $MyInvocation.MyCommand.Path
$assets = Split-Path -Parent $source
$root = Split-Path -Parent $assets
$scenarioSource = Join-Path $assets "team-test-bundle"
$stage = Join-Path $assets "team-test-bundle-stage"
$output = Join-Path $assets "output\Fabric_Migration_Readiness_Assistant_Team_Test_Bundle.zip"

if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Path $stage | Out-Null

$htmlPath = Join-Path $stage "Fabric_Migration_Readiness_Assistant.html"
Copy-Item (Join-Path $root "index.html") $htmlPath
Copy-Item (Join-Path $scenarioSource "*") $stage

$html = [IO.File]::ReadAllText($htmlPath)
$assessedState = [IO.File]::ReadAllText((Join-Path $scenarioSource "Fabrikam_Mixed_Assessed_State.json")).Trim()
$pattern = 'const sampleState = \{.*?\r?\n    \};\r?\n    let state'
$replacement = "const sampleState = $assessedState;`r`n    let state"
$packagedHtml = [regex]::Replace($html, $pattern, $replacement, [Text.RegularExpressions.RegexOptions]::Singleline)
if ($packagedHtml -eq $html) { throw "Could not inject the assessed test state into the packaged HTML." }
$packagedHtml = $packagedHtml.Replace('id="sampleBtn">Load sample</button>', 'id="sampleBtn">Load assessed sample</button>')
[IO.File]::WriteAllText($htmlPath, $packagedHtml, [Text.UTF8Encoding]::new($false))

$version = @(
    "Fabric Migration Readiness Assistant - Team Test Bundle"
    "Built: $((Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'))"
    "Source commit: $(git -C $root rev-parse --short HEAD)"
    "Open Fabric_Migration_Readiness_Assistant.html to begin."
)
Set-Content -Path (Join-Path $stage "VERSION.txt") -Value $version -Encoding utf8

if (Test-Path $output) { Remove-Item $output -Force }
Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $output -CompressionLevel Optimal
Remove-Item $stage -Recurse -Force

Write-Host "Generated $output"
