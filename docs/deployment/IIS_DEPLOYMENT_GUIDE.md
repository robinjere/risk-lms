# IIS Deployment Guide - Risk LMS
## Co-operative Bank of Tanzania PLC

This guide provides step-by-step instructions for deploying the Risk LMS Django application on IIS (Internet Information Services) on Windows Server.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Server Preparation](#2-server-preparation)
3. [Install Python](#3-install-python)
4. [Install IIS Components](#4-install-iis-components)
5. [Configure wfastcgi](#5-configure-wfastcgi)
6. [Deploy Application Files](#6-deploy-application-files)
7. [Configure IIS Website](#7-configure-iis-website)
8. [Configure Application Pool](#8-configure-application-pool)
9. [Set Environment Variables](#9-set-environment-variables)
10. [Database Setup](#10-database-setup)
11. [Static Files Configuration](#11-static-files-configuration)
12. [SSL Certificate Setup](#12-ssl-certificate-setup)
13. [Testing the Deployment](#13-testing-the-deployment)
14. [Troubleshooting](#14-troubleshooting)

---

## 1. Prerequisites

### Hardware Requirements
- Windows Server 2016/2019/2022
- Minimum 4GB RAM (8GB recommended)
- 50GB available disk space
- Network access to SQL Server

### Software Requirements
- Windows Server with IIS role installed
- Python 3.9 or higher
- Microsoft SQL Server 2016+ (can be on separate server)
- ODBC Driver 17 for SQL Server
- Network connectivity to Active Directory servers

### Network Requirements
- Port 80 (HTTP) open
- Port 443 (HTTPS) open
- Port 389 (LDAP) access to AD servers
- Port 1433 (SQL Server) or named instance port

---

## 2. Server Preparation

### 2.1 Update Windows Server
```powershell
# Run Windows Update
Install-WindowsUpdate -AcceptAll -AutoReboot
```

### 2.2 Create Application Directory
```powershell
# Create the web application directory
New-Item -Path "C:\inetpub\wwwroot\risk_lms" -ItemType Directory -Force

# Create logs directory
New-Item -Path "C:\inetpub\wwwroot\risk_lms\logs" -ItemType Directory -Force

# Create media directories
New-Item -Path "C:\inetpub\wwwroot\risk_lms\media\videos" -ItemType Directory -Force
New-Item -Path "C:\inetpub\wwwroot\risk_lms\media\certificates" -ItemType Directory -Force
New-Item -Path "C:\inetpub\wwwroot\risk_lms\media\course_thumbnails" -ItemType Directory -Force
New-Item -Path "C:\inetpub\wwwroot\risk_lms\media\interactive_courses" -ItemType Directory -Force
```

---

## 3. Install Python

### 3.1 Download and Install Python
1. Download Python 3.11 from https://www.python.org/downloads/
2. Run installer with these options:
   - ☑️ **Install for all users**
   - ☑️ **Add Python to PATH**
   - Install to: `C:\Python311`

### 3.2 Verify Installation
```powershell
python --version
# Should show: Python 3.11.x

pip --version
# Should show pip version
```

### 3.3 Install Required Python Packages
```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install Django and dependencies
pip install -r C:\inetpub\wwwroot\risk_lms\requirements.txt

# Install wfastcgi for IIS integration
pip install wfastcgi
```

---

## 4. Install IIS Components

### 4.1 Install IIS Role and Features
Run in **PowerShell as Administrator**:

```powershell
# Install IIS with required features
Install-WindowsFeature -Name Web-Server -IncludeManagementTools

# Install additional IIS features
Install-WindowsFeature -Name `
    Web-CGI, `
    Web-ISAPI-Ext, `
    Web-ISAPI-Filter, `
    Web-Includes, `
    Web-Http-Errors, `
    Web-Common-Http, `
    Web-Performance, `
    Web-Basic-Auth, `
    Web-Windows-Auth, `
    Web-Security, `
    Web-Filtering, `
    Web-Stat-Compression, `
    Web-Dyn-Compression, `
    Web-Mgmt-Console

# Install URL Rewrite Module (download separately)
# Download from: https://www.iis.net/downloads/microsoft/url-rewrite
```

### 4.2 Install URL Rewrite Module
1. Download from: https://www.iis.net/downloads/microsoft/url-rewrite
2. Run the installer
3. Restart IIS: `iisreset`

---

## 5. Configure wfastcgi

### 5.1 Enable wfastcgi
Run in **PowerShell as Administrator**:

```powershell
# Enable wfastcgi
wfastcgi-enable

# This will output something like:
# "C:\Python311\python.exe|C:\Python311\Lib\site-packages\wfastcgi.py" can now be used as a FastCGI script processor
```

### 5.2 Configure FastCGI Settings
```powershell
# Add Python to FastCGI configuration
& "$env:windir\system32\inetsrv\appcmd.exe" set config -section:system.webServer/fastCgi /+"[fullPath='C:\Python311\python.exe',arguments='C:\Python311\Lib\site-packages\wfastcgi.py']"

# Set activity timeout (for long-running requests)
& "$env:windir\system32\inetsrv\appcmd.exe" set config -section:system.webServer/fastCgi /[fullPath='C:\Python311\python.exe',arguments='C:\Python311\Lib\site-packages\wfastcgi.py'].activityTimeout:600

# Set request timeout
& "$env:windir\system32\inetsrv\appcmd.exe" set config -section:system.webServer/fastCgi /[fullPath='C:\Python311\python.exe',arguments='C:\Python311\Lib\site-packages\wfastcgi.py'].requestTimeout:600
```

---

## 6. Deploy Application Files

### 6.1 Copy Application Files
Copy the entire Risk LMS project to the server:

```powershell
# If copying from network share
Copy-Item -Path "\\SourceServer\Share\risk_lms\*" -Destination "C:\inetpub\wwwroot\risk_lms" -Recurse -Force

# Or use robocopy for large files
robocopy "\\SourceServer\Share\risk_lms" "C:\inetpub\wwwroot\risk_lms" /E /Z /MT:8
```

### 6.2 Set Directory Permissions
```powershell
# Grant IIS_IUSRS permissions to application directory
$acl = Get-Acl "C:\inetpub\wwwroot\risk_lms"
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule("IIS_IUSRS", "Modify", "ContainerInherit,ObjectInherit", "None", "Allow")
$acl.SetAccessRule($rule)
Set-Acl "C:\inetpub\wwwroot\risk_lms" $acl

# Grant full control to media folder (for uploads)
$acl = Get-Acl "C:\inetpub\wwwroot\risk_lms\media"
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule("IIS_IUSRS", "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow")
$acl.SetAccessRule($rule)
Set-Acl "C:\inetpub\wwwroot\risk_lms\media" $acl

# Grant permissions to logs folder
$acl = Get-Acl "C:\inetpub\wwwroot\risk_lms\logs"
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule("IIS_IUSRS", "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow")
$acl.SetAccessRule($rule)
Set-Acl "C:\inetpub\wwwroot\risk_lms\logs" $acl
```

---

## 7. Configure IIS Website

### 7.1 Create Website in IIS Manager

1. Open **IIS Manager** (`inetmgr`)
2. Right-click **Sites** → **Add Website**
3. Configure:
   - **Site name**: `RiskLMS`
   - **Physical path**: `C:\inetpub\wwwroot\risk_lms`
   - **Binding Type**: `http`
   - **IP Address**: `All Unassigned`
   - **Port**: `80`
   - **Host name**: `risklms.cbtbank.co.tz` (or your domain)

### 7.2 Using PowerShell
```powershell
# Create the website
Import-Module WebAdministration

# Remove default website binding on port 80 (optional)
# Remove-WebBinding -Name "Default Web Site" -Port 80

# Create new website
New-Website -Name "RiskLMS" `
    -PhysicalPath "C:\inetpub\wwwroot\risk_lms" `
    -Port 80 `
    -HostHeader "risklms.cbtbank.co.tz"
```

### 7.3 Configure Handler Mappings
In IIS Manager:
1. Select **RiskLMS** site
2. Double-click **Handler Mappings**
3. Click **Add Module Mapping**
4. Configure:
   - **Request path**: `*`
   - **Module**: `FastCgiModule`
   - **Executable**: `C:\Python311\python.exe|C:\Python311\Lib\site-packages\wfastcgi.py`
   - **Name**: `Django FastCGI`

---

## 8. Configure Application Pool

### 8.1 Create Application Pool
```powershell
# Create new application pool
New-WebAppPool -Name "RiskLMSPool"

# Configure application pool settings
Set-ItemProperty -Path "IIS:\AppPools\RiskLMSPool" -Name "managedRuntimeVersion" -Value ""
Set-ItemProperty -Path "IIS:\AppPools\RiskLMSPool" -Name "enable32BitAppOnWin64" -Value $false
Set-ItemProperty -Path "IIS:\AppPools\RiskLMSPool" -Name "processModel.identityType" -Value "ApplicationPoolIdentity"

# Set recycling options
Set-ItemProperty -Path "IIS:\AppPools\RiskLMSPool" -Name "recycling.periodicRestart.time" -Value "00:00:00"
Set-ItemProperty -Path "IIS:\AppPools\RiskLMSPool" -Name "recycling.periodicRestart.schedule" -Value @{value="03:00:00"}

# Assign pool to website
Set-ItemProperty -Path "IIS:\Sites\RiskLMS" -Name "applicationPool" -Value "RiskLMSPool"
```

### 8.2 Configure Pool Identity for SQL Server
If using Windows Authentication with SQL Server:

1. Open **IIS Manager**
2. Select **Application Pools** → **RiskLMSPool**
3. Click **Advanced Settings**
4. Under **Process Model** → **Identity**
5. Select **Custom account**
6. Enter domain account: `KCBLTZ\ServiceAccount`
7. Enter password

Or use PowerShell:
```powershell
Set-ItemProperty -Path "IIS:\AppPools\RiskLMSPool" -Name "processModel.identityType" -Value "SpecificUser"
Set-ItemProperty -Path "IIS:\AppPools\RiskLMSPool" -Name "processModel.userName" -Value "KCBLTZ\ServiceAccount"
Set-ItemProperty -Path "IIS:\AppPools\RiskLMSPool" -Name "processModel.password" -Value "ServicePassword"
```

---

## 9. Set Environment Variables

### 9.1 System Environment Variables
Set these at the system level:

```powershell
# Set environment variables for Django
[System.Environment]::SetEnvironmentVariable("DJANGO_ENV", "production", "Machine")
[System.Environment]::SetEnvironmentVariable("SECRET_KEY", "your-super-secure-secret-key-min-50-chars", "Machine")
[System.Environment]::SetEnvironmentVariable("DEBUG", "False", "Machine")
[System.Environment]::SetEnvironmentVariable("ALLOWED_HOSTS", "risklms.cbtbank.co.tz,localhost,192.168.10.100", "Machine")

# Database settings
[System.Environment]::SetEnvironmentVariable("DB_ENGINE", "mssql", "Machine")
[System.Environment]::SetEnvironmentVariable("DB_NAME", "risk_lms", "Machine")
[System.Environment]::SetEnvironmentVariable("DB_HOST", "DBSERVER\SQLEXPRESS", "Machine")

# Certificate URL
[System.Environment]::SetEnvironmentVariable("CERTIFICATE_BASE_URL", "https://risklms.cbtbank.co.tz", "Machine")

# Restart IIS to pick up environment variables
iisreset
```

### 9.2 Generate Secure Secret Key
```powershell
# Generate a secure secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 10. Database Setup

### 10.1 Create Database
On SQL Server, run:

```sql
-- Create database
CREATE DATABASE risk_lms;
GO

-- If using SQL Authentication, create user
CREATE LOGIN risk_lms_user WITH PASSWORD = 'StrongPassword123!';
GO

USE risk_lms;
CREATE USER risk_lms_user FOR LOGIN risk_lms_user;
ALTER ROLE db_owner ADD MEMBER risk_lms_user;
GO

-- If using Windows Authentication, grant access to IIS App Pool identity
-- Replace 'IIS APPPOOL\RiskLMSPool' with your app pool name
USE risk_lms;
CREATE USER [IIS APPPOOL\RiskLMSPool] FOR LOGIN [IIS APPPOOL\RiskLMSPool];
ALTER ROLE db_owner ADD MEMBER [IIS APPPOOL\RiskLMSPool];
GO
```

### 10.2 Run Migrations
```powershell
cd C:\inetpub\wwwroot\risk_lms

# Set environment variables
$env:DJANGO_ENV = "production"
$env:DB_ENGINE = "mssql"
$env:DB_HOST = "DBSERVER\SQLEXPRESS"

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

---

## 11. Static Files Configuration

### 11.1 Collect Static Files
```powershell
cd C:\inetpub\wwwroot\risk_lms
python manage.py collectstatic --noinput
```

### 11.2 Configure Static File Handler
Add to `web.config` or configure in IIS:

```xml
<configuration>
    <system.webServer>
        <handlers>
            <!-- Serve static files directly -->
            <add name="StaticFile" path="static/*" verb="*" modules="StaticFileModule" resourceType="File" requireAccess="Read" />
            <add name="MediaFile" path="media/*" verb="*" modules="StaticFileModule" resourceType="File" requireAccess="Read" />
        </handlers>
    </system.webServer>
</configuration>
```

### 11.3 Create Virtual Directories (Alternative)
In IIS Manager:
1. Right-click **RiskLMS** site
2. Add Virtual Directory:
   - **Alias**: `static`
   - **Physical path**: `C:\inetpub\wwwroot\risk_lms\staticfiles`
3. Add another Virtual Directory:
   - **Alias**: `media`
   - **Physical path**: `C:\inetpub\wwwroot\risk_lms\media`

---

## 12. SSL Certificate Setup

### 12.1 Option A: Use Internal CA Certificate
If your bank has an internal Certificate Authority:

1. Request certificate from IT Security team
2. Import certificate to server
3. Bind to website

### 12.2 Option B: Create Self-Signed Certificate (Testing Only)
```powershell
# Create self-signed certificate
New-SelfSignedCertificate -DnsName "risklms.cbtbank.co.tz" -CertStoreLocation "cert:\LocalMachine\My"

# Get certificate thumbprint
$cert = Get-ChildItem -Path Cert:\LocalMachine\My | Where-Object {$_.Subject -like "*risklms*"}
$cert.Thumbprint
```

### 12.3 Bind SSL Certificate to Website
```powershell
# Add HTTPS binding
New-WebBinding -Name "RiskLMS" -Protocol "https" -Port 443 -HostHeader "risklms.cbtbank.co.tz"

# Bind certificate
$cert = Get-ChildItem -Path Cert:\LocalMachine\My | Where-Object {$_.Subject -like "*risklms*"}
$binding = Get-WebBinding -Name "RiskLMS" -Protocol "https"
$binding.AddSslCertificate($cert.Thumbprint, "My")
```

### 12.4 Force HTTPS Redirect
Add to `web.config`:
```xml
<rewrite>
    <rules>
        <rule name="HTTP to HTTPS redirect" stopProcessing="true">
            <match url="(.*)" />
            <conditions>
                <add input="{HTTPS}" pattern="off" ignoreCase="true" />
            </conditions>
            <action type="Redirect" url="https://{HTTP_HOST}/{R:1}" redirectType="Permanent" />
        </rule>
    </rules>
</rewrite>
```

---

## 13. Testing the Deployment

### 13.1 Test Checklist
```powershell
# 1. Check IIS is running
Get-Service W3SVC

# 2. Check application pool is running
Get-WebAppPoolState -Name "RiskLMSPool"

# 3. Test website locally
Invoke-WebRequest -Uri "http://localhost" -UseBasicParsing

# 4. Check Django configuration
cd C:\inetpub\wwwroot\risk_lms
python manage.py check --deploy
```

### 13.2 Test URLs
- Homepage: `https://risklms.cbtbank.co.tz/`
- Admin: `https://risklms.cbtbank.co.tz/admin/`
- Login: `https://risklms.cbtbank.co.tz/accounts/login/`

### 13.3 Test Login
1. Try logging in with AD credentials
2. Verify user is created in database
3. Check role assignment

---

## 14. Troubleshooting

### 14.1 Common Issues

#### Issue: 500 Internal Server Error
```powershell
# Check IIS logs
Get-Content "C:\inetpub\logs\LogFiles\W3SVC1\*.log" -Tail 50

# Check Django error log
Get-Content "C:\inetpub\wwwroot\risk_lms\logs\django_error.log" -Tail 50

# Enable detailed errors temporarily
# In web.config, set: <httpErrors errorMode="Detailed" />
```

#### Issue: Static Files Not Loading
```powershell
# Verify static files collected
Test-Path "C:\inetpub\wwwroot\risk_lms\staticfiles"

# Check permissions
icacls "C:\inetpub\wwwroot\risk_lms\staticfiles"

# Recollect static files
python manage.py collectstatic --clear --noinput
```

#### Issue: Database Connection Failed
```powershell
# Test SQL Server connection
sqlcmd -S "DBSERVER\SQLEXPRESS" -d risk_lms -Q "SELECT 1"

# Check ODBC driver
Get-OdbcDriver | Where-Object {$_.Name -like "*SQL Server*"}

# Test from Python
python -c "import pyodbc; print(pyodbc.drivers())"
```

#### Issue: LDAP Authentication Failed
```powershell
# Test AD connectivity
Test-NetConnection -ComputerName "192.168.10.50" -Port 389

# Test LDAP bind
python -c "
from ldap3 import Server, Connection
server = Server('192.168.10.50', port=389)
conn = Connection(server, 'KCBLTZ\\testuser', 'password')
print(conn.bind())
"
```

### 14.2 Restart Procedures
```powershell
# Restart application pool only
Restart-WebAppPool -Name "RiskLMSPool"

# Restart entire IIS
iisreset

# Restart specific website
Stop-Website -Name "RiskLMS"
Start-Website -Name "RiskLMS"
```

### 14.3 Log Locations
| Log Type | Location |
|----------|----------|
| IIS Logs | `C:\inetpub\logs\LogFiles\W3SVC1\` |
| Django Errors | `C:\inetpub\wwwroot\risk_lms\logs\django_error.log` |
| Security Logs | `C:\inetpub\wwwroot\risk_lms\logs\security.log` |
| Windows Events | Event Viewer → Windows Logs → Application |

---

## Quick Reference Commands

```powershell
# ===== Common Operations =====

# Check website status
Get-Website -Name "RiskLMS"

# Check app pool status
Get-WebAppPoolState -Name "RiskLMSPool"

# Restart app pool
Restart-WebAppPool -Name "RiskLMSPool"

# View recent IIS logs
Get-Content "C:\inetpub\logs\LogFiles\W3SVC1\*.log" -Tail 100

# Run Django management commands
cd C:\inetpub\wwwroot\risk_lms
$env:DJANGO_ENV = "production"
python manage.py <command>

# Update static files after code changes
python manage.py collectstatic --noinput
Restart-WebAppPool -Name "RiskLMSPool"
```

---

## Deployment Checklist

- [ ] Python 3.11 installed at C:\Python311
- [ ] IIS role installed with CGI feature
- [ ] URL Rewrite module installed
- [ ] wfastcgi installed and enabled
- [ ] Application files copied to C:\inetpub\wwwroot\risk_lms
- [ ] Directory permissions set for IIS_IUSRS
- [ ] Website created in IIS
- [ ] Application pool configured
- [ ] Environment variables set
- [ ] Database created and migrated
- [ ] Static files collected
- [ ] SSL certificate installed
- [ ] HTTPS binding configured
- [ ] Superuser created
- [ ] Login tested with AD credentials
- [ ] File uploads tested
- [ ] Certificate generation tested

---

## Support Information

**IT Support Contact**: IT Department  
**System Administrator**: Risk Management & Compliance Team  
**Documentation Version**: 1.0  
**Last Updated**: December 19, 2025

---

© 2025 Co-operative Bank of Tanzania PLC. All rights reserved.
