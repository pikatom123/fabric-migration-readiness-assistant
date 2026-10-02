$ErrorActionPreference = "Stop"

$source = Split-Path -Parent $MyInvocation.MyCommand.Path
$assets = Split-Path -Parent $source
$root = Split-Path -Parent $assets
$scenarioSource = Join-Path $assets "team-test-bundle"
$stage = Join-Path $assets "team-test-bundle-stage"
$output = Join-Path $assets "output\Fabric_Migration_Readiness_Assistant_Team_Test_Bundle.zip"

if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Path $stage | Out-Null

Copy-Item (Join-Path $root "index.html") (Join-Path $stage "Fabric_Migration_Readiness_Assistant.html")
Copy-Item (Join-Path $scenarioSource "*") $stage

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
