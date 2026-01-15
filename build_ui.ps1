$ErrorActionPreference = "Stop"

$repoRoot = $PSScriptRoot
$frontendDir = Join-Path $repoRoot "frontend"
$backendUiDir = Join-Path $repoRoot "backend\agent_demo_framework\ui"
$distDir = Join-Path $backendUiDir "dist"
$srcDir = Join-Path $backendUiDir "src"

Write-Host "Building frontend UI..."
Push-Location $frontendDir
npm install
npm run build
Pop-Location

Write-Host "Copying UI artifacts into package..."
New-Item -ItemType Directory -Force $distDir | Out-Null
New-Item -ItemType Directory -Force $srcDir | Out-Null

Copy-Item -Recurse -Force (Join-Path $frontendDir "dist\*") $distDir
Copy-Item -Recurse -Force (Join-Path $frontendDir "src\*") $srcDir

Write-Host "Done."
