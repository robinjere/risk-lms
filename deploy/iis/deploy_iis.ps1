# =============================================================================
# Risk LMS - IIS Deployment Script
# Co-operative Bank of Tanzania PLC
# Run this script as Administrator on the Windows Server
# =============================================================================

param(
    [string]$SiteName = "RiskLMS",
    [string]$AppPoolName = "RiskLMSPool",
    [string]$PhysicalPath = "C:\inetpub\wwwroot\risk_lms",
    [string]$HostName = "risklms.cbtbank.co.tz",
    [string]$PythonPath = "C:\Python311",
    [string]$DBServer = "Martin\SQLEXPRESS",
    [string]$DBName = "risk_lms"
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Risk LMS - IIS Deployment Script" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    exit 1
}

# =============================================================================
# Step 1: Verify Prerequisites
# =============================================================================
Write-Host "Step 1: Verifying prerequisites..." -ForegroundColor Yellow

# Check Python installation
if (Test-Path "$PythonPath\python.exe") {
    $pythonVersion = & "$PythonPath\python.exe" --version 2>&1
    Write-Host "  [OK] Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Python not found at $PythonPath" -ForegroundColor Red
    Write-Host "  Please install Python 3.11 to $PythonPath" -ForegroundColor Red
    exit 1
}

# Check IIS
if (Get-Service W3SVC -ErrorAction SilentlyContinue) {
    Write-Host "  [OK] IIS is installed" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] IIS is not installed" -ForegroundColor Red
    Write-Host "  Run: Install-WindowsFeature -Name Web-Server -IncludeManagementTools" -ForegroundColor Yellow
    exit 1
}

# Check WebAdministration module
if (Get-Module -ListAvailable -Name WebAdministration) {
    Import-Module WebAdministration
    Write-Host "  [OK] WebAdministration module loaded" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] WebAdministration module not available" -ForegroundColor Red
    exit 1
}

Write-Host ""

# =============================================================================
# Step 2: Create Directory Structure
# =============================================================================
Write-Host "Step 2: Creating directory structure..." -ForegroundColor Yellow

$directories = @(
    $PhysicalPath,
    "$PhysicalPath\logs",
    "$PhysicalPath\media",
    "$PhysicalPath\media\videos",
    "$PhysicalPath\media\certificates",
    "$PhysicalPath\media\course_thumbnails",
    "$PhysicalPath\media\interactive_courses",
    "$PhysicalPath\staticfiles"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -Path $dir -ItemType Directory -Force | Out-Null
        Write-Host "  [CREATED] $dir" -ForegroundColor Green
    } else {
        Write-Host "  [EXISTS] $dir" -ForegroundColor Cyan
    }
}

Write-Host ""

# =============================================================================
# Step 3: Install Python Packages
# =============================================================================
Write-Host "Step 3: Installing Python packages..." -ForegroundColor Yellow

& "$PythonPath\python.exe" -m pip install --upgrade pip 2>&1 | Out-Null
Write-Host "  [OK] pip upgraded" -ForegroundColor Green

# Install wfastcgi
& "$PythonPath\python.exe" -m pip install wfastcgi 2>&1 | Out-Null
Write-Host "  [OK] wfastcgi installed" -ForegroundColor Green

# Install requirements if requirements.txt exists
if (Test-Path "$PhysicalPath\requirements.txt") {
    Write-Host "  Installing requirements from requirements.txt..." -ForegroundColor Cyan
    & "$PythonPath\python.exe" -m pip install -r "$PhysicalPath\requirements.txt" 2>&1 | Out-Null
    Write-Host "  [OK] Requirements installed" -ForegroundColor Green
}

Write-Host ""

# =============================================================================
# Step 4: Enable wfastcgi
# =============================================================================
Write-Host "Step 4: Configuring wfastcgi..." -ForegroundColor Yellow

# Enable wfastcgi
$wfastcgiPath = "$PythonPath\Lib\site-packages\wfastcgi.py"
if (Test-Path $wfastcgiPath) {
    # Configure FastCGI
    $fastcgiConfig = "$PythonPath\python.exe|$wfastcgiPath"
    
    # Remove existing FastCGI configuration if exists
    $existingConfig = & "$env:windir\system32\inetsrv\appcmd.exe" list config -section:system.webServer/fastCgi 2>&1
    if ($existingConfig -match [regex]::Escape($PythonPath)) {
        & "$env:windir\system32\inetsrv\appcmd.exe" set config -section:system.webServer/fastCgi /-"[fullPath='$PythonPath\python.exe']" 2>&1 | Out-Null
    }
    
    # Add FastCGI configuration
    & "$env:windir\system32\inetsrv\appcmd.exe" set config -section:system.webServer/fastCgi /+"[fullPath='$PythonPath\python.exe',arguments='$wfastcgiPath',maxInstances='4',idleTimeout='300',activityTimeout='600',requestTimeout='600']" 2>&1 | Out-Null
    
    Write-Host "  [OK] FastCGI configured" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] wfastcgi.py not found at $wfastcgiPath" -ForegroundColor Red
    exit 1
}

Write-Host ""

# =============================================================================
# Step 5: Create Application Pool
# =============================================================================
Write-Host "Step 5: Creating Application Pool..." -ForegroundColor Yellow

# Remove existing app pool if exists
if (Test-Path "IIS:\AppPools\$AppPoolName") {
    Remove-WebAppPool -Name $AppPoolName -ErrorAction SilentlyContinue
    Write-Host "  [REMOVED] Existing app pool: $AppPoolName" -ForegroundColor Yellow
}

# Create new app pool
New-WebAppPool -Name $AppPoolName | Out-Null

# Configure app pool
Set-ItemProperty -Path "IIS:\AppPools\$AppPoolName" -Name "managedRuntimeVersion" -Value ""
Set-ItemProperty -Path "IIS:\AppPools\$AppPoolName" -Name "enable32BitAppOnWin64" -Value $false
Set-ItemProperty -Path "IIS:\AppPools\$AppPoolName" -Name "processModel.identityType" -Value "ApplicationPoolIdentity"
Set-ItemProperty -Path "IIS:\AppPools\$AppPoolName" -Name "processModel.idleTimeout" -Value "00:00:00"
Set-ItemProperty -Path "IIS:\AppPools\$AppPoolName" -Name "startMode" -Value "AlwaysRunning"

Write-Host "  [OK] Application Pool created: $AppPoolName" -ForegroundColor Green

Write-Host ""

# =============================================================================
# Step 6: Create Website
# =============================================================================
Write-Host "Step 6: Creating Website..." -ForegroundColor Yellow

# Remove existing site if exists
if (Get-Website -Name $SiteName -ErrorAction SilentlyContinue) {
    Remove-Website -Name $SiteName -ErrorAction SilentlyContinue
    Write-Host "  [REMOVED] Existing website: $SiteName" -ForegroundColor Yellow
}

# Create website
New-Website -Name $SiteName `
    -PhysicalPath $PhysicalPath `
    -ApplicationPool $AppPoolName `
    -Port 80 `
    -HostHeader $HostName | Out-Null

# Add localhost binding for testing
New-WebBinding -Name $SiteName -Protocol "http" -Port 80 -HostHeader "localhost" -ErrorAction SilentlyContinue | Out-Null

Write-Host "  [OK] Website created: $SiteName" -ForegroundColor Green
Write-Host "  [OK] Bindings: $HostName:80, localhost:80" -ForegroundColor Green

Write-Host ""

# =============================================================================
# Step 7: Configure Handler Mapping
# =============================================================================
Write-Host "Step 7: Configuring Handler Mapping..." -ForegroundColor Yellow

# Add Python handler
$handler = @{
    name = "Python FastCGI"
    path = "*"
    verb = "*"
    modules = "FastCgiModule"
    scriptProcessor = "$PythonPath\python.exe|$wfastcgiPath"
    resourceType = "Unspecified"
    requireAccess = "Script"
}

# Remove existing handler if exists
Remove-WebHandler -Name "Python FastCGI" -PSPath "IIS:\Sites\$SiteName" -ErrorAction SilentlyContinue

# Add new handler
Add-WebHandler -Name $handler.name `
    -Path $handler.path `
    -Verb $handler.verb `
    -Modules $handler.modules `
    -ScriptProcessor $handler.scriptProcessor `
    -ResourceType $handler.resourceType `
    -RequiredAccess Script `
    -PSPath "IIS:\Sites\$SiteName"

Write-Host "  [OK] Handler mapping configured" -ForegroundColor Green

Write-Host ""

# =============================================================================
# Step 8: Set Directory Permissions
# =============================================================================
Write-Host "Step 8: Setting directory permissions..." -ForegroundColor Yellow

$identity = "IIS AppPool\$AppPoolName"

# Grant permissions to application directory
$acl = Get-Acl $PhysicalPath
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule($identity, "ReadAndExecute", "ContainerInherit,ObjectInherit", "None", "Allow")
$acl.AddAccessRule($rule)
Set-Acl $PhysicalPath $acl
Write-Host "  [OK] Read/Execute permissions set on $PhysicalPath" -ForegroundColor Green

# Grant full control to media directory
$acl = Get-Acl "$PhysicalPath\media"
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule($identity, "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow")
$acl.AddAccessRule($rule)
Set-Acl "$PhysicalPath\media" $acl
Write-Host "  [OK] Full control permissions set on media folder" -ForegroundColor Green

# Grant full control to logs directory
$acl = Get-Acl "$PhysicalPath\logs"
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule($identity, "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow")
$acl.AddAccessRule($rule)
Set-Acl "$PhysicalPath\logs" $acl
Write-Host "  [OK] Full control permissions set on logs folder" -ForegroundColor Green

Write-Host ""

# =============================================================================
# Step 9: Set Environment Variables
# =============================================================================
Write-Host "Step 9: Setting environment variables..." -ForegroundColor Yellow

# Generate a secure secret key
$secretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 50 | ForEach-Object {[char]$_})

[System.Environment]::SetEnvironmentVariable("DJANGO_ENV", "production", "Machine")
[System.Environment]::SetEnvironmentVariable("SECRET_KEY", $secretKey, "Machine")
[System.Environment]::SetEnvironmentVariable("DEBUG", "False", "Machine")
[System.Environment]::SetEnvironmentVariable("ALLOWED_HOSTS", "$HostName,localhost,127.0.0.1", "Machine")
[System.Environment]::SetEnvironmentVariable("DB_ENGINE", "mssql", "Machine")
[System.Environment]::SetEnvironmentVariable("DB_NAME", $DBName, "Machine")
[System.Environment]::SetEnvironmentVariable("DB_HOST", $DBServer, "Machine")
[System.Environment]::SetEnvironmentVariable("CERTIFICATE_BASE_URL", "https://$HostName", "Machine")

Write-Host "  [OK] Environment variables set" -ForegroundColor Green
Write-Host "  [INFO] SECRET_KEY has been auto-generated" -ForegroundColor Cyan

Write-Host ""

# =============================================================================
# Step 10: Run Django Setup
# =============================================================================
Write-Host "Step 10: Running Django setup..." -ForegroundColor Yellow

# Set environment variables for this session
$env:DJANGO_ENV = "production"
$env:SECRET_KEY = $secretKey
$env:DEBUG = "False"
$env:DB_ENGINE = "mssql"
$env:DB_NAME = $DBName
$env:DB_HOST = $DBServer
$env:ALLOWED_HOSTS = "$HostName,localhost,127.0.0.1"

Push-Location $PhysicalPath

# Collect static files
Write-Host "  Collecting static files..." -ForegroundColor Cyan
& "$PythonPath\python.exe" manage.py collectstatic --noinput 2>&1 | Out-Null
Write-Host "  [OK] Static files collected" -ForegroundColor Green

# Run migrations
Write-Host "  Running database migrations..." -ForegroundColor Cyan
& "$PythonPath\python.exe" manage.py migrate 2>&1 | Out-Null
Write-Host "  [OK] Database migrations complete" -ForegroundColor Green

Pop-Location

Write-Host ""

# =============================================================================
# Step 11: Start Website
# =============================================================================
Write-Host "Step 11: Starting website..." -ForegroundColor Yellow

Start-WebAppPool -Name $AppPoolName
Start-Website -Name $SiteName

Write-Host "  [OK] Application pool started" -ForegroundColor Green
Write-Host "  [OK] Website started" -ForegroundColor Green

Write-Host ""

# =============================================================================
# Deployment Complete
# =============================================================================
Write-Host "============================================" -ForegroundColor Green
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Website Information:" -ForegroundColor Cyan
Write-Host "  Site Name:      $SiteName"
Write-Host "  App Pool:       $AppPoolName"
Write-Host "  Physical Path:  $PhysicalPath"
Write-Host "  URL (Local):    http://localhost/"
Write-Host "  URL (Network):  http://$HostName/"
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Configure SSL certificate for HTTPS"
Write-Host "  2. Create superuser: python manage.py createsuperuser"
Write-Host "  3. Configure DNS to point $HostName to this server"
Write-Host "  4. Test login with AD credentials"
Write-Host ""
Write-Host "To create a superuser, run:" -ForegroundColor Cyan
Write-Host "  cd $PhysicalPath"
Write-Host "  `$env:DJANGO_ENV = 'production'"
Write-Host "  `$env:DB_ENGINE = 'mssql'"
Write-Host "  `$env:DB_HOST = '$DBServer'"
Write-Host "  $PythonPath\python.exe manage.py createsuperuser"
Write-Host ""
