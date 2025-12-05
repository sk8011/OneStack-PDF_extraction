@echo off
echo ========================================
echo   OCR Dependencies Installation Helper
echo ========================================
echo.
echo This script will guide you through installing:
echo   1. Tesseract OCR (text recognition)
echo   2. Poppler (PDF to image conversion)
echo.
echo Both are required for extracting data from image-based PDFs.
echo.

:MENU
echo ----------------------------------------
echo   Select what to install:
echo ----------------------------------------
echo   1. Install Tesseract OCR
echo   2. Install Poppler
echo   3. Install Both
echo   4. Verify Installation
echo   5. Exit
echo ----------------------------------------
set /p choice="Enter choice (1-5): "

if "%choice%"=="1" goto TESSERACT
if "%choice%"=="2" goto POPPLER
if "%choice%"=="3" goto BOTH
if "%choice%"=="4" goto VERIFY
if "%choice%"=="5" goto END
goto MENU

:TESSERACT
echo.
echo ========================================
echo   Installing Tesseract OCR
echo ========================================
echo.
echo Opening the download page in your browser...
start https://github.com/UB-Mannheim/tesseract/wiki
echo.
echo Instructions:
echo 1. Download: tesseract-ocr-w64-setup-x.x.x.xxxx.exe
echo 2. Run the installer
echo 3. Default path: C:\Program Files\Tesseract-OCR
echo 4. Add to PATH (see Step 5 below)
echo.
pause
goto PATH_INSTRUCTIONS

:POPPLER
echo.
echo ========================================
echo   Installing Poppler
echo ========================================
echo.
echo Opening the download page in your browser...
start https://github.com/oschwartz10612/poppler-windows/releases
echo.
echo Instructions:
echo 1. Download: Release-xx.xx.x-0.zip
echo 2. Extract the ZIP file
echo 3. Copy the extracted folder to C:\poppler
echo    (so you have C:\poppler\Library\bin\pdftoppm.exe)
echo 4. Add C:\poppler\Library\bin to PATH (see Step 5 below)
echo.
echo Alternative: Place the 'poppler' folder in:
echo   %~dp0
echo.
pause
goto PATH_INSTRUCTIONS

:BOTH
echo.
echo Installing both Tesseract and Poppler...
echo.
echo ========================================
echo   Step 1: Tesseract OCR
echo ========================================
start https://github.com/UB-Mannheim/tesseract/wiki
echo.
echo Download and install Tesseract OCR first.
echo Default path: C:\Program Files\Tesseract-OCR
echo.
pause
echo.
echo ========================================
echo   Step 2: Poppler
echo ========================================
start https://github.com/oschwartz10612/poppler-windows/releases
echo.
echo Download and extract Poppler.
echo Extract to: C:\poppler (so you have C:\poppler\Library\bin)
echo.
pause
goto PATH_INSTRUCTIONS

:PATH_INSTRUCTIONS
echo.
echo ========================================
echo   Step: Add to System PATH
echo ========================================
echo.
echo 1. Press Win + R, type 'sysdm.cpl' and press Enter
echo 2. Click "Advanced" tab
echo 3. Click "Environment Variables"
echo 4. Under "System variables", find "Path" and click "Edit"
echo 5. Click "New" and add these paths:
echo.
echo    C:\Program Files\Tesseract-OCR
echo    C:\poppler\Library\bin
echo.
echo 6. Click OK to save all dialogs
echo 7. RESTART your command prompt/terminal
echo.
pause
goto VERIFY

:VERIFY
echo.
echo ========================================
echo   Verifying Installation
echo ========================================
echo.
echo Checking Tesseract...
tesseract --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Tesseract is installed
    tesseract --version 2>&1 | findstr /C:"tesseract"
) else (
    echo [X] Tesseract NOT found in PATH
)
echo.
echo Checking Poppler (pdftoppm)...
pdftoppm -v >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Poppler is installed
    pdftoppm -v 2>&1 | findstr /C:"pdftoppm"
) else (
    echo [X] Poppler NOT found in PATH
    echo     Looking for local poppler folder...
    if exist "%~dp0poppler\Library\bin\pdftoppm.exe" (
        echo [OK] Found local poppler at %~dp0poppler\Library\bin
    ) else if exist "%~dp0poppler\bin\pdftoppm.exe" (
        echo [OK] Found local poppler at %~dp0poppler\bin
    ) else (
        echo [X] Local poppler not found
    )
)
echo.
echo ========================================
if %errorlevel% equ 0 (
    echo   All checks passed! OCR should work.
) else (
    echo   Some components missing. Please install them.
)
echo ========================================
echo.
pause
goto MENU

:END
echo.
echo Goodbye!
pause
