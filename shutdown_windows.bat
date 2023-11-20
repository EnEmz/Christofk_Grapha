@echo off
echo Shutting down the Dash app...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr "LISTENING" ^| findstr ":8050"') do (
    taskkill /f /pid %%a
)
echo Server shut down.
pause