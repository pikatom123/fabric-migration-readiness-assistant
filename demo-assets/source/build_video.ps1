$ErrorActionPreference = "Stop"

$source = Split-Path -Parent $MyInvocation.MyCommand.Path
$assets = Split-Path -Parent $source
$frames = Join-Path $source "frames"
$output = Join-Path $assets "output"
$audio = Join-Path $output "Fabric_Migration_Readiness_Assistant_Narration.wav"
$video = Join-Path $output "Fabric_Migration_Readiness_Assistant_2min_Demo.mp4"

$ffmpeg = (Get-Command ffmpeg -ErrorAction Stop).Source
$durations = @(11, 14, 15, 16, 16, 16, 18, 14)
$names = @("00-title", "01-problem", "02-inputs", "03-discovery", "04-inventory", "05-assessment", "06-summary", "07-impact")

$arguments = @("-y")
for ($index = 0; $index -lt $names.Count; $index++) {
    $arguments += @("-loop", "1", "-t", [string]$durations[$index], "-i", (Join-Path $frames ($names[$index] + ".png")))
}
$arguments += @("-i", $audio)

$filters = @()
for ($index = 0; $index -lt $names.Count; $index++) {
    $fadeOut = $durations[$index] - 0.5
    $filters += "[$index`:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p,fade=t=in:st=0:d=0.5,fade=t=out:st=$fadeOut`:d=0.5,setpts=PTS-STARTPTS[v$index]"
}
$videoInputs = (0..($names.Count - 1) | ForEach-Object { "[v$_]" }) -join ""
$filters += "$videoInputs`concat=n=$($names.Count):v=1:a=0[v]"
$filters += "[8:a]adelay=1500|1500,apad=pad_dur=10[a]"

$arguments += @(
    "-filter_complex", ($filters -join ";"),
    "-map", "[v]", "-map", "[a]",
    "-t", "120", "-r", "30",
    "-c:v", "libx264", "-preset", "medium", "-crf", "20",
    "-c:a", "aac", "-b:a", "192k",
    "-movflags", "+faststart",
    $video
)

& $ffmpeg @arguments
if ($LASTEXITCODE -ne 0) { throw "FFmpeg failed with exit code $LASTEXITCODE" }
Write-Host "Generated $video"
