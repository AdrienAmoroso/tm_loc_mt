@echo off
REM ============================================================================
REM Tennis Manager Localization Translation Tool
REM ============================================================================
REM
REM This batch file runs the translation pipeline for Tennis Manager.
REM It handles virtual environment activation and Python execution.
REM
REM Usage: Double-click this file to start translation
REM
REM ============================================================================

setlocal enabledelayedexpansion

REM Get the directory where this script is located
cd /d "%~dp0"

REM Go back to the project root (one level up from scripts)
cd ..

REM Check if virtual environment exists
if not exist ".\.venv\Scripts\python.exe" (
    echo.
    echo ====================================================================
    echo ERROR: Virtual environment not found
    echo ====================================================================
    echo.
    echo Please run this command in PowerShell to set up the environment:
    echo.
    echo   python -m venv .venv
    echo   .\.venv\Scripts\pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".\.env" (
    echo.
    echo ====================================================================
    echo WARNING: .env file not found
    echo ====================================================================
    echo.
    echo Create a .env file with your API key:
    echo.
    echo   GEMINI_API_KEY=your_key_here
    echo   or
    echo   OPENAI_API_KEY=your_key_here
    echo.
    pause
)

REM Clear screen
cls

REM Run the translation pipeline
echo.
echo ====================================================================
echo Tennis Manager Localization Translation
echo ====================================================================
echo.
echo Starting translation pipeline...
echo.

.\.venv\Scripts\python.exe translate_loc_refactored.py

REM Capture exit code
set EXIT_CODE=%ERRORLEVEL%

echo.
if %EXIT_CODE% equ 0 (
    echo ====================================================================
    echo Translation completed successfully!
    echo ====================================================================
) else (
    echo ====================================================================
    echo Translation failed with exit code %EXIT_CODE%
    echo ====================================================================
    echo.
    echo Check the logs directory for details:
    echo   logs/mt_run_*.log
    echo.
)

echo.
echo Press any key to close this window...
pause >nul

exit /b %EXIT_CODE%
