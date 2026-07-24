@echo off
echo ========================================
echo   Starting Jiangcheng Carbon Eye Pro...
echo ========================================
cd /d "%~dp0"

:: Activate virtual environment
call "D:\桌面\hongniao_study\.venv\Scripts\activate.bat"

:: Start Streamlit
"D:\桌面\hongniao_study\.venv\Scripts\python.exe" -m streamlit run ui/app.py

pause
