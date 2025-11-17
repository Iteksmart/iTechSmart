# iTechSmart Agent Installation Script for Windows
# Copyright © 2025 iTechSmart Inc. All rights reserved.

param(
    [Parameter(Mandatory=$true)]
    [string]$ApiKey,
    
    [Parameter(Mandatory=$false)]
    [string]$Organization = "",
    
    [Parameter(Mandatory=$false)]
    [string]$AgentName = $env:COMPUTERNAME
)

$ErrorActionPreference = "Stop"

# Variables
$Version = "1.0.0"
$BinaryName = "itechsmart-agent.exe"
$InstallDir = "C:\Program Files\iTechSmart"
$ConfigDir = "C:\ProgramData\iTechSmart"
$LogDir = "C:\ProgramData\iTechSmart\logs"
$ServiceName = "iTechSmartAgent"

Write-Host "========================================" -ForegroundColor Green
Write-Host "iTechSmart Agent Installation" -ForegroundColor Green
Write-Host "Version: $Version" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "ERROR: Please run as Administrator" -ForegroundColor Red
    exit 1
}

# Create directories
Write-Host "Creating directories..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
New-Item -ItemType Directory -Force -Path $ConfigDir | Out-Null
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

# Download binary
Write-Host "Downloading iTechSmart Agent..." -ForegroundColor Green
$DownloadUrl = "https://github.com/Iteksmart/iTechSmart/releases/download/v$Version/itechsmart-agent-windows-amd64.exe"
$BinaryPath = Join-Path $InstallDir $BinaryName

try {
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $BinaryPath
} catch {
    Write-Host "ERROR: Failed to download agent: $_" -ForegroundColor Red
    exit 1
}

# Create configuration file
Write-Host "Creating configuration..." -ForegroundColor Green
$ConfigPath = Join-Path $ConfigDir "agent.yaml"
$ConfigContent = @"
# iTechSmart Agent Configuration
agent_name: "$AgentName"
organization: "$Organization"
server_url: "https://api.itechsmart.dev"
websocket_url: "wss://api.itechsmart.dev/agent/ws"
api_key: "$ApiKey"

# Collection intervals (seconds)
system_metrics_interval: 60
security_check_interval: 3600
software_inventory_interval: 86400

# Features
enable_system_monitoring: true
enable_security_checks: true
enable_software_inventory: true
enable_remote_commands: true
enable_patch_management: true
enable_audit_logging: true

# Logging
log_level: "info"
log_file: "$LogDir\agent.log"

# Product integration
ninja_enabled: true
enterprise_enabled: true
"@

Set-Content -Path $ConfigPath -Value $ConfigContent

# Install as Windows Service
Write-Host "Installing as Windows Service..." -ForegroundColor Green

# Stop service if it exists
$existingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "Stopping existing service..." -ForegroundColor Yellow
    Stop-Service -Name $ServiceName -Force
    Start-Sleep -Seconds 2
}

# Create service using sc.exe
$ServiceCommand = "`"$BinaryPath`" --config `"$ConfigPath`""
$result = sc.exe create $ServiceName binPath= $ServiceCommand start= auto DisplayName= "iTechSmart Agent"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create service" -ForegroundColor Red
    exit 1
}

# Set service description
sc.exe description $ServiceName "iTechSmart Agent - System monitoring and management"

# Start service
Write-Host "Starting service..." -ForegroundColor Green
Start-Service -Name $ServiceName

# Wait for service to start
Start-Sleep -Seconds 3

# Check service status
$service = Get-Service -Name $ServiceName
if ($service.Status -eq "Running") {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Installation Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Agent installed to: $BinaryPath"
    Write-Host "Configuration: $ConfigPath"
    Write-Host "Logs: $LogDir\agent.log"
    Write-Host ""
    Write-Host "Service Status: Running" -ForegroundColor Green
    Write-Host ""
    Write-Host "The iTechSmart Agent is now monitoring your system!" -ForegroundColor Green
    Write-Host "View logs: Get-Content '$LogDir\agent.log' -Tail 50 -Wait"
    Write-Host ""
} else {
    Write-Host "WARNING: Service installed but not running" -ForegroundColor Yellow
    Write-Host "Status: $($service.Status)"
    Write-Host "Try starting manually: Start-Service $ServiceName"
}