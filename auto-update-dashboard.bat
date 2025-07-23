@echo off
echo ========================================
echo GitHub Contribution Dashboard Automation
echo ========================================
echo Starting automated update process...
echo.

cd /d "C:\Users\Lenovo\Rahuljoshi07"

echo Running Node.js automation script...
node auto-update-dashboard.js

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS: Dashboard updated successfully!
    echo ========================================
    echo Check your GitHub profile: https://github.com/Rahuljoshi07
) else (
    echo.
    echo ========================================
    echo ERROR: Dashboard update failed!
    echo ========================================
    echo Check the error messages above for details.
)

echo.
echo Press any key to exit...
pause > nul
