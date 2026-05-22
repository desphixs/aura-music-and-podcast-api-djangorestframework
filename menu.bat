@echo off
cd /d "%~dp0"

:menu
echo ==========================================
echo        BACKEND CONTROL PANEL
echo ==========================================
echo 1. Start venv
echo 2. Run Server
echo 3. Make Migrations and Migrate
echo 4. Open Admin
echo 5. Update requirements.txt
echo 6. Deactivate venv
echo 7. Exit
echo ==========================================

set /p choice="Choose option: "

if "%choice%"=="1" (
    if exist venv\Scripts\activate.bat (
        call venv\Scripts\activate.bat
        echo Virtual environment activated!
    ) else (
        echo Error: venv folder not found!
    )
    exit /b
)

if "%choice%"=="2" (
    python manage.py runserver
    exit /b
)

if "%choice%"=="3" (
    python manage.py makemigrations
    python manage.py migrate
    exit /b
)

if "%choice%"=="4" (
    start http://127.0.0.1:8000/admin
    exit /b
)

if "%choice%"=="5" (
    pip freeze > requirements.txt
    echo requirements.txt updated!
    exit /b
)


if "%choice%"=="6" (
    if exist venv\Scripts\activate.bat (
        call venv\Scripts\deactivate.bat
        echo Virtual environment deactivated!
    ) else (
        echo Error: venv folder not found!
    )
    exit /b
)


if "%choice%"=="7" (
    exit /b
)

:: If invalid choice, just exit to terminal
exit /b