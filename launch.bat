@echo off
title Team Task Manager Launcher
color 0a

echo ===================================================
echo       Starting Team Task Manager Application
echo ===================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python to run this application.
    pause
    exit /b
)

:: Check if dependencies need to be installed
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Flask not found. Installing dependencies...
    cd backend
    pip install -r requirements.txt
    cd ..
)

echo [INFO] Starting the backend server...
:: Start the server in a separate command window
start "Team Task Manager Backend" cmd /c "cd backend && python app.py"

echo [INFO] Waiting for the server to initialize...
timeout /t 3 /nobreak > nul

echo [INFO] Opening your default web browser...
start http://localhost:5000/

echo.
echo ===================================================
echo Application is now running in your browser!
echo To stop the application, simply close the new 
echo command window that was opened.
echo ===================================================
echo.
pause
