@echo off
REM Quick Git Commit ^& Push Script
REM Usage: Just type "g" in this folder

echo.
echo ================================
echo   Quick Git Commit ^& Push
echo ================================
echo.

REM Stage all changes
echo Staging all changes...
git add .

REM Show what's being committed
echo.
echo Changes to be committed:
git status --short
echo.

REM Prompt for commit message
set /p message=Enter commit message: 

REM Check if message is empty
if "%message%"=="" (
    echo Error: Commit message cannot be empty!
    exit /b 1
)

REM Commit with the message
echo.
echo Committing...
git commit -m "%message%"

REM Push to remote
echo.
echo Pushing to remote...
git push -u origin HEAD

echo.
echo ================================
echo   Done!
echo ================================
