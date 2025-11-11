@echo off
echo Creating Odoo module directory structure...

:: Define the base module directory
set BASE_DIR=addons\warehouse_barcode_scanner

:: Create main module directory
mkdir %BASE_DIR%

:: Create top-level files
type nul > %BASE_DIR%\__init__.py
type nul > %BASE_DIR%\__manifest__.py

:: Create controllers directory and its __init__.py and main.py
mkdir %BASE_DIR%\controllers
type nul > %BASE_DIR%\controllers\__init__.py
type nul > %BASE_DIR%\controllers\main.py

:: Create models directory and its __init__.py
mkdir %BASE_DIR%\models
type nul > %BASE_DIR%\models\__init__.py

:: Create static assets directories and files
mkdir %BASE_DIR%\static\src\components
mkdir %BASE_DIR%\static\src\xml
mkdir %BASE_DIR%\static\css

type nul > %BASE_DIR%\static\src\components\barcode_scanner.js
type nul > %BASE_DIR%\static\src\xml\barcode_scanner.xml
type nul > %BASE_DIR%\static\css\barcode_scanner.css

:: Create views directory and its stock_views.xml
mkdir %BASE_DIR%\views
type nul > %BASE_DIR%\views\stock_views.xml

echo Directory structure and files created successfully in %BASE_DIR%.
pause
