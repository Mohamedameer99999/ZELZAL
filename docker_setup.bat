@echo off
chcp 65001 >nul
title ZELZAL Docker Setup
echo ============================================
echo    ZELZAL - Docker Setup
echo ============================================
echo.

where docker >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker is not installed.
    echo Download: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

echo [1/3] Building Docker image...
docker build -t zelzal:latest .

echo [2/3] Starting container...
docker compose up -d

echo [3/3] Done!
echo.
echo Open: http://localhost:5000
echo Login: admin / admin123
echo.
pause
