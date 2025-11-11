<#
.SYNOPSIS
    Creates the directory and file structure for a new Odoo module.
.DESCRIPTION
    This script scaffolds a new Odoo module with a specified structure, including nested static
    directories, data, and report folders. It checks if the module directory
    already exists to prevent overwriting.
.EXAMPLE
    .\Create-KPI-Module.ps1
    This will create the 'kpi_performance' module structure in the current directory.
#>

# --- Configuration ---
$moduleName = "amg_crm_kpi"

# --- Script Body ---
$modulePath = Join-Path -Path (Get-Location) -ChildPath $moduleName

# Check if the module directory already exists
if (Test-Path -Path $modulePath) {
    Write-Warning "Directory '$moduleName' already exists in this location. Aborting script."
    return
}

Write-Host "Creating module structure for '$moduleName' at: $modulePath" -ForegroundColor Cyan

try {
    # Create root directory
    $null = New-Item -Path $modulePath -ItemType Directory

    # Create root files
    Write-Host "Creating root files..."
    $null = New-Item -Path (Join-Path $modulePath "__init__.py") -ItemType File
    $null = New-Item -Path (Join-Path $modulePath "__manifest__.py") -ItemType File

    # Create primary sub-directories
    Write-Host "Creating primary sub-directories..."
    $subDirs = @("models", "security", "views", "data", "static", "reports")
    foreach ($dir in $subDirs) {
        $null = New-Item -Path (Join-Path $modulePath $dir) -ItemType Directory
    }

    # Create files within 'models'
    Write-Host "Creating model files..."
    $null = New-Item -Path (Join-Path $modulePath "models/__init__.py") -ItemType File
    $null = New-Item -Path (Join-Path $modulePath "models/kpi_type.py") -ItemType File
    $null = New-Item -Path (Join-Path $modulePath "models/kpi_target.py") -ItemType File
    $null = New-Item -Path (Join-Path $modulePath "models/kpi_evaluation.py") -ItemType File
    $null = New-Item -Path (Join-Path $modulePath "models/kpi_achievement.py") -ItemType File
    $null = New-Item -Path (Join-Path $modulePath "models/kpi_dashboard.py") -ItemType File

    # Create files within 'security'
    Write-Host "Creating security files..."
    $null = New-Item -Path (Join-Path $modulePath "security/ir.model.access.csv") -ItemType File
    $null = New-Item -Path (Join-Path $modulePath "security/kpi_security.xml") -ItemType File

    # Create files within 'views'
    Write-Host "Creating view files..."
    $null = New-Item -Path (Join-Path $modulePath "views/kpi_type_views.xml") -ItemType File
    $null = New-Item -Path (Join-Path $modulePath "views/kpi_target_views.xml") -ItemType File
    $null = New-Item -Path (Join-Path $modulePath "views/kpi_evaluation_views.xml") -ItemType File
    $null = New-Item -Path (Join-Path $modulePath "views/kpi_achievement_views.xml") -ItemType File
    $null = New-Item -Path (Join-Path $modulePath "views/kpi_dashboard_views.xml") -ItemType File
    $null = New-Item -Path (Join-Path $modulePath "views/menus.xml") -ItemType File

    # Create files within 'data'
    Write-Host "Creating data files..."
    $null = New-Item -Path (Join-Path $modulePath "data/kpi_data.xml") -ItemType File

    # Create structure and files within 'static'
    Write-Host "Creating static directory structure and files..."
    $staticSrcPath = New-Item -Path (Join-Path $modulePath "static/src") -ItemType Directory
    $null = New-Item -Path (Join-Path $staticSrcPath "js") -ItemType Directory
    $null = New-Item -Path (Join-Path $staticSrcPath "css") -ItemType Directory
    $null = New-Item -Path (Join-Path $staticSrcPath "js/kpi_dashboard.js") -ItemType File
    $null = New-Item -Path (Join-Path $staticSrcPath "css/kpi_styles.css") -ItemType File

    # Create files within 'reports'
    Write-Host "Creating report files..."
    $null = New-Item -Path (Join-Path $modulePath "reports/kpi_reports.py") -ItemType File
    $null = New-Item -Path (Join-Path $modulePath "reports/kpi_report_templates.xml") -ItemType File


    Write-Host "----------------------------------------"
    Write-Host "Successfully created the module structure for '$moduleName'." -ForegroundColor Green
    Write-Host "----------------------------------------"

    # Display the final structure
    # The 'tree' command is available on Windows. For PowerShell 7+ on any OS, or for older versions,
    # 'Get-ChildItem' is the native alternative.
    if (Get-Command tree -ErrorAction SilentlyContinue) {
        tree /F $modulePath
    } else {
        Get-ChildItem -Path $modulePath -Recurse | ForEach-Object { $_.FullName.Replace($PWD.Path + "\", "") }
    }

}
catch {
    Write-Error "An error occurred during module creation: $_"
}