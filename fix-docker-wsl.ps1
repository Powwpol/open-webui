# Pulsai Docker WSL2 Fix Script
# Fixes common Docker Desktop WSL2 issues on Windows

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   Pulsai Docker WSL2 Fix Script" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "WARNING: Not running as Administrator" -ForegroundColor Yellow
    Write-Host "Some fixes require Administrator privileges" -ForegroundColor Yellow
    Write-Host ""
}

# Step 1: Stop Docker Desktop
Write-Host "Step 1: Stopping Docker Desktop..." -ForegroundColor Blue
Stop-Process -Name "Docker Desktop" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
Write-Host "Done" -ForegroundColor Green
Write-Host ""

# Step 2: Clean Docker cache
Write-Host "Step 2: Cleaning Docker cache..." -ForegroundColor Blue
try {
    docker system prune -af --volumes 2>&1 | Out-Null
    Write-Host "Docker cache cleaned" -ForegroundColor Green
} catch {
    Write-Host "Docker not responding, continuing..." -ForegroundColor Yellow
}
Write-Host ""

# Step 3: Shutdown WSL
Write-Host "Step 3: Shutting down WSL..." -ForegroundColor Blue
wsl --shutdown
Start-Sleep -Seconds 5
Write-Host "Done" -ForegroundColor Green
Write-Host ""

# Step 4: Check disk space
Write-Host "Step 4: Checking disk space..." -ForegroundColor Blue
$dockerDataPath = "$env:LOCALAPPDATA\Docker\wsl\data"
if (Test-Path $dockerDataPath) {
    $vhdxPath = "$dockerDataPath\ext4.vhdx"
    if (Test-Path $vhdxPath) {
        $vhdxSize = (Get-Item $vhdxPath).Length / 1GB
        Write-Host "Docker VHDX size: $([math]::Round($vhdxSize, 2)) GB" -ForegroundColor Cyan
        
        if ($vhdxSize -gt 200) {
            Write-Host "WARNING: VHDX is very large (>200GB)" -ForegroundColor Yellow
            Write-Host "Consider optimizing or resetting Docker data" -ForegroundColor Yellow
        }
    }
}
$drive = (Get-Item $env:LOCALAPPDATA).PSDrive.Name + ":"
$freeSpace = (Get-PSDrive $drive).Free / 1GB
Write-Host "Free disk space on ${drive}: $([math]::Round($freeSpace, 2)) GB" -ForegroundColor Cyan
if ($freeSpace -lt 10) {
    Write-Host "WARNING: Low disk space (<10GB)" -ForegroundColor Red
    Write-Host "Docker may fail to build. Free up disk space!" -ForegroundColor Red
}
Write-Host ""

# Step 5: Compact VHDX (requires admin)
if ($isAdmin -and (Test-Path $vhdxPath)) {
    Write-Host "Step 5: Compacting Docker VHDX..." -ForegroundColor Blue
    Write-Host "This may take several minutes..." -ForegroundColor Yellow
    
    $diskpartScript = @"
select vdisk file="$vhdxPath"
attach vdisk readonly
compact vdisk
detach vdisk
"@
    
    $diskpartScript | diskpart | Out-Null
    Write-Host "VHDX compacted" -ForegroundColor Green
} else {
    Write-Host "Step 5: Skipping VHDX compact (requires admin)" -ForegroundColor Yellow
}
Write-Host ""

# Step 6: Increase WSL memory limit
Write-Host "Step 6: Checking WSL configuration..." -ForegroundColor Blue
$wslConfigPath = "$env:USERPROFILE\.wslconfig"
$wslConfigExists = Test-Path $wslConfigPath

if (-not $wslConfigExists) {
    Write-Host "Creating .wslconfig with recommended settings..." -ForegroundColor Yellow
    $wslConfig = @"
[wsl2]
memory=8GB
processors=4
swap=2GB
localhostForwarding=true
"@
    $wslConfig | Out-File -FilePath $wslConfigPath -Encoding utf8
    Write-Host "Created $wslConfigPath" -ForegroundColor Green
} else {
    Write-Host ".wslconfig already exists" -ForegroundColor Green
    Write-Host "Current configuration:" -ForegroundColor Cyan
    Get-Content $wslConfigPath | Write-Host
}
Write-Host ""

# Step 7: Clean temp files
Write-Host "Step 7: Cleaning temp files..." -ForegroundColor Blue
$tempPath = "$env:TEMP\docker-*"
Remove-Item -Path $tempPath -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "Temp files cleaned" -ForegroundColor Green
Write-Host ""

# Step 8: Restart Docker Desktop
Write-Host "Step 8: Restarting Docker Desktop..." -ForegroundColor Blue
$dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
if (Test-Path $dockerPath) {
    Start-Process $dockerPath
    Write-Host "Docker Desktop starting..." -ForegroundColor Green
    Write-Host "Waiting 30 seconds for Docker to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
} else {
    Write-Host "Docker Desktop executable not found" -ForegroundColor Red
    Write-Host "Please start Docker Desktop manually" -ForegroundColor Yellow
}
Write-Host ""

# Step 9: Verify Docker
Write-Host "Step 9: Verifying Docker..." -ForegroundColor Blue
$maxRetries = 10
$retry = 0
while ($retry -lt $maxRetries) {
    try {
        docker info 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Docker is running!" -ForegroundColor Green
            break
        }
    } catch {}
    
    $retry++
    Write-Host "Waiting for Docker... ($retry/$maxRetries)" -ForegroundColor Yellow
    Start-Sleep -Seconds 3
}

if ($retry -eq $maxRetries) {
    Write-Host "Docker failed to start" -ForegroundColor Red
    Write-Host "Try restarting Docker Desktop manually" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   Fix Complete" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Verify Docker is running:" -ForegroundColor White
Write-Host "   docker info" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Clean build (without cache):" -ForegroundColor White
Write-Host "   .\build-pulsai.bat --no-cache --slim" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. If still failing, try:" -ForegroundColor White
Write-Host "   - Restart your computer" -ForegroundColor Cyan
Write-Host "   - Reset Docker to factory defaults" -ForegroundColor Cyan
Write-Host "   - Update Docker Desktop" -ForegroundColor Cyan
Write-Host ""
Write-Host "For slim build (faster, no embeddings):" -ForegroundColor Yellow
Write-Host "   .\build-pulsai.bat --slim" -ForegroundColor Cyan
Write-Host ""

