@echo off
REM ==========================================================================
REM  HomeGuard Security System - launcher
REM  Double-click this file to run the simulator.
REM  Author: Nnanyelugo Ahukannah
REM ==========================================================================

REM Move to the folder this .bat lives in, so it works no matter where it's
REM launched from (%~dp0 = the drive + path of this script).
cd /d "%~dp0"

echo Starting HomeGuard Security System...
echo.

REM Try the Windows Python launcher first, then fall back to "python".
where py >nul 2>nul
if %errorlevel%==0 (
    py homeguard_system.py
) else (
    python homeguard_system.py
)

REM Remember whether the simulator succeeded before we print the footer.
set "exitcode=%errorlevel%"

echo.
if not "%exitcode%"=="0" (
    echo [ERROR] The simulator exited with code %exitcode%.
    echo Make sure Python is installed and on your PATH.
)

echo.
echo Simulation finished. Press any key to close this window...
REM "pause" keeps the window open so you can read the output after double-click.
pause >nul
