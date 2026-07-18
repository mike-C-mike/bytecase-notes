param(
    [string]$Version = "0.9.0"
)

$ErrorActionPreference = "Stop"

$AppName = "ByteCaseNotes"
$ReleaseRoot = Join-Path $PSScriptRoot "release"
$ReleaseName = "$AppName-v$Version"
$ReleaseDir = Join-Path $ReleaseRoot $ReleaseName
$ZipPath = Join-Path $ReleaseRoot "$ReleaseName.zip"
$ChecksumPath = Join-Path $ReleaseRoot "$ReleaseName-SHA256SUMS.txt"

Write-Host "Building $ReleaseName..."

if (Test-Path $ReleaseDir) { Remove-Item $ReleaseDir -Recurse -Force }
if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }
if (Test-Path $ChecksumPath) { Remove-Item $ChecksumPath -Force }

New-Item -ItemType Directory -Force -Path $ReleaseRoot | Out-Null

py -m pip install -r requirements-build.txt
py -m PyInstaller --clean --noconfirm .\bytecase-notes.spec

New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null
Copy-Item .\dist\ByteCaseNotes.exe $ReleaseDir
Copy-Item .\README.md $ReleaseDir
Copy-Item .\DEPENDENCIES.md $ReleaseDir
Copy-Item .\KNOWN_LIMITATIONS.md $ReleaseDir
Copy-Item .\UNSIGNED_WINDOWS_NOTICE.md $ReleaseDir
Copy-Item .\SIMPLE_WORKFLOW.md $ReleaseDir
Copy-Item .\LICENSE $ReleaseDir

Compress-Archive -Path (Join-Path $ReleaseDir "*") -DestinationPath $ZipPath -Force

$ZipHash = Get-FileHash $ZipPath -Algorithm SHA256
$ExeHash = Get-FileHash (Join-Path $ReleaseDir "ByteCaseNotes.exe") -Algorithm SHA256

@(
    "$($ZipHash.Hash)  $($ZipHash.Path | Split-Path -Leaf)",
    "$($ExeHash.Hash)  ByteCaseNotes.exe"
) | Set-Content -Path $ChecksumPath -Encoding UTF8

Write-Host "Release folder: $ReleaseDir"
Write-Host "Release ZIP: $ZipPath"
Write-Host "Checksums: $ChecksumPath"
