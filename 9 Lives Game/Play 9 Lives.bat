@echo off
title 9 Lives
cd /d "%~dp0"
if exist "dist\9 Lives\9 Lives.exe" (
    start "" "dist\9 Lives\9 Lives.exe"
    exit
)
start "" python "9 Lives.py"
exit
