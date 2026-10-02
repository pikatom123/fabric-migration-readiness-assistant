$ErrorActionPreference = "Stop"

$source = Split-Path -Parent $MyInvocation.MyCommand.Path
$assets = Split-Path -Parent $source
$root = Split-Path -Parent $assets
$packageSource = Join-Path $assets "complete-package"
$scenarioSource = Join-Path $assets "team-test-bundle"
$stage = Join-Path $assets "complete-package-stage"
$kitName = "Fabric_Migration_Readiness_Assistant_CSA_Kit"
$kit = Join-Path $stage $kitName
$output = Join-Path $assets "output\Fabric_Migration_Readiness_Assistant_CSA_Enablement_Kit.zip"

if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Path $kit | Out-Null

$folders = @(
	"01-Presentation",
	"02-Video",
	"03-Prototype-and-Testing\scenarios",
	"04-Future-Architecture",
	"05-Copilot-Workspace\.github\skills",
	"05-Copilot-Workspace\.github\agents",
	"05-Copilot-Workspace\.vscode",
	"06-Assessment-Engine"
)
foreach ($folder in $folders) {
	New-Item -ItemType Directory -Path (Join-Path $kit $folder) -Force | Out-Null
}

Copy-Item (Join-Path $packageSource "START_HERE.md") $kit
Copy-Item (Join-Path $packageSource "INSTALL_SKILL.md") $kit

Copy-Item (Join-Path $assets "output\Fabric_Migration_Readiness_Assistant_Hackathon_Deck.pptx") (Join-Path $kit "01-Presentation")
Copy-Item (Join-Path $assets "output\Fabric_Migration_Readiness_Assistant_Demo_Script.txt") (Join-Path $kit "01-Presentation")
Copy-Item (Join-Path $assets "output\Fabric_Migration_Readiness_Assistant_2min_Demo.mp4") (Join-Path $kit "02-Video")
Copy-Item (Join-Path $assets "output\Fabric_Migration_Readiness_Assistant_Narration.txt") (Join-Path $kit "02-Video")

Copy-Item (Join-Path $root "index.html") (Join-Path $kit "03-Prototype-and-Testing\Fabric_Migration_Readiness_Assistant.html")
Copy-Item (Join-Path $scenarioSource "*") (Join-Path $kit "03-Prototype-and-Testing\scenarios")

Copy-Item (Join-Path $root "docs\FUTURE_ARCHITECTURE.md") (Join-Path $kit "04-Future-Architecture")
Copy-Item (Join-Path $root "docs\CSA_REUSE_PLAYBOOK.md") (Join-Path $kit "04-Future-Architecture")

Copy-Item (Join-Path $root ".github\skills\fabric-adoption-readiness") (Join-Path $kit "05-Copilot-Workspace\.github\skills") -Recurse
Copy-Item (Join-Path $root ".github\agents\fabric-adoption-discovery.agent.md") (Join-Path $kit "05-Copilot-Workspace\.github\agents")
Copy-Item (Join-Path $root ".vscode\mcp.json") (Join-Path $kit "05-Copilot-Workspace\.vscode")

Copy-Item (Join-Path $root "src") (Join-Path $kit "06-Assessment-Engine") -Recurse
Copy-Item (Join-Path $root "tests") (Join-Path $kit "06-Assessment-Engine") -Recurse
Copy-Item (Join-Path $root "examples") (Join-Path $kit "06-Assessment-Engine") -Recurse
Copy-Item (Join-Path $root "pyproject.toml") (Join-Path $kit "06-Assessment-Engine")
Copy-Item (Join-Path $root "README.md") (Join-Path $kit "06-Assessment-Engine")
Copy-Item (Join-Path $root "TESTING.md") (Join-Path $kit "06-Assessment-Engine")

Get-ChildItem $kit -Directory -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force

$version = @(
	"Fabric Migration Readiness and Optimisation Assistant - Complete CSA Enablement Kit"
	"Built: $((Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'))"
	"Source commit: $(git -C $root rev-parse --short HEAD)"
	"Engine version: $((Select-String -Path (Join-Path $root 'pyproject.toml') -Pattern '^version = ').Line.Split('"')[1])"
	"Start with START_HERE.md."
)
Set-Content -Path (Join-Path $kit "VERSION.txt") -Value $version -Encoding utf8

$manifest = Get-ChildItem $kit -Recurse -File | Sort-Object FullName | ForEach-Object {
	[PSCustomObject]@{
		Path = $_.FullName.Substring($kit.Length + 1).Replace("\", "/")
		Bytes = $_.Length
		SHA256 = (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
	}
}
$manifest | Export-Csv (Join-Path $kit "ARTIFACT_MANIFEST.csv") -NoTypeInformation -Encoding utf8

if (Test-Path $output) { Remove-Item $output -Force }
Compress-Archive -Path $kit -DestinationPath $output -CompressionLevel Optimal
Remove-Item $stage -Recurse -Force

Write-Host "Generated $output"
