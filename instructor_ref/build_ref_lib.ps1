$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$src = Join-Path $PSScriptRoot "cdma_ref.cpp"
$outDir = Join-Path $repoRoot "ref"

if (-not (Test-Path $src)) {
    throw "Missing source file: $src"
}

New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$gpp = Get-Command g++ -ErrorAction SilentlyContinue
if (-not $gpp) {
    throw "g++ was not found in PATH. Install a C++ toolchain (e.g., MinGW-w64) and retry."
}

$isWindows = ($env:OS -eq "Windows_NT")
$isMacOS = $false
if (-not $isWindows -and $PSVersionTable.PSVersion.Major -ge 6 -and $PSVersionTable.OS) {
    $isMacOS = $PSVersionTable.OS -match "Darwin"
}

if ($isWindows) {
    $outLib = Join-Path $outDir "cdma_ref.dll"
    $buildArgs = @("-shared", "-O2", $src, "-o", $outLib)
} elseif ($isMacOS) {
    $outLib = Join-Path $outDir "libcdma_ref.dylib"
    $buildArgs = @("-shared", "-fPIC", "-O2", $src, "-o", $outLib)
} else {
    $outLib = Join-Path $outDir "libcdma_ref.so"
    $buildArgs = @("-shared", "-fPIC", "-O2", $src, "-o", $outLib)
}

Write-Host "Building reference library..."
& $gpp.Source @buildArgs

if ($LASTEXITCODE -ne 0 -or -not (Test-Path $outLib)) {
    throw "Build failed."
}

Write-Host "Done: $outLib"
