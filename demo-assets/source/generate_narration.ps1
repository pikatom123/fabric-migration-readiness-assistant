$ErrorActionPreference = "Stop"

$source = Split-Path -Parent $MyInvocation.MyCommand.Path
$assets = Split-Path -Parent $source
$output = Join-Path $assets "output"
$textPath = Join-Path $output "Fabric_Migration_Readiness_Assistant_Narration.txt"
$audioPath = Join-Path $output "Fabric_Migration_Readiness_Assistant_Narration.wav"

Add-Type -AssemblyName System.Speech
$synthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synthesizer.SelectVoice("Microsoft Hazel Desktop")
$synthesizer.Rate = 3
$synthesizer.Volume = 100
$synthesizer.SetOutputToWaveFile($audioPath)
$synthesizer.Speak((Get-Content $textPath -Raw))
$synthesizer.Dispose()

Write-Host "Generated $audioPath"