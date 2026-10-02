$ErrorActionPreference = "Stop"

$source = Split-Path -Parent $MyInvocation.MyCommand.Path
$assets = Split-Path -Parent $source
$output = Join-Path $assets "output"
$walkthrough = Join-Path $assets "walkthrough"
$raw = Get-ChildItem (Join-Path $walkthrough "raw\*.webm") | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$roadmap = Join-Path $walkthrough "roadmap.png"
$audio = Join-Path $output "Fabric_Migration_Readiness_Assistant_Narration.wav"
$video = Join-Path $output "Fabric_Migration_Readiness_Assistant_2min_Demo.mp4"

$ffmpegCommand = Get-Command ffmpeg -ErrorAction SilentlyContinue
if ($ffmpegCommand) {
    $ffmpeg = $ffmpegCommand.Source
} else {
    $ffmpeg = Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Filter ffmpeg.exe -Recurse | Select-Object -First 1 -ExpandProperty FullName
}
if (-not $ffmpeg) { throw "FFmpeg was not found." }
if (-not $raw) { throw "No raw Playwright recording was found." }
if (-not (Test-Path $roadmap)) { throw "Roadmap frame was not found." }

$ffprobe = Join-Path (Split-Path -Parent $ffmpeg) "ffprobe.exe"
$rawDuration = [double](& $ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $raw.FullName)
$speed = $rawDuration / 103
$audioDuration = [double](& $ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $audio)
$audioSpeed = $audioDuration / 118.5

$filters = @(
    "[0:v]setpts=PTS/$speed,scale=1728:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#f7f6f2,setsar=1,fps=30,format=yuv420p[walkthrough]",
    "[1:v]scale=1920:1080,setsar=1,fps=30,format=yuv420p,fade=t=in:st=0:d=0.4[roadmap]",
    "[walkthrough][roadmap]concat=n=2:v=1:a=0[v]",
    "[2:a]atempo=$audioSpeed,adelay=500|500,apad=pad_dur=10[a]"
)

$arguments = @(
    "-y",
    "-i", $raw.FullName,
    "-loop", "1", "-t", "17", "-i", $roadmap,
    "-i", $audio,
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
Write-Host "Generated $video from $($raw.Name)"
