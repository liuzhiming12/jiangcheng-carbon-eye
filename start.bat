@echo off  
echo ========================================
echo   Starting Jiangcheng Carbon Eye Pro...
echo   江城碳眼Pro 启动中...
echo ========================================
cd /d "%~dp0"
python -m streamlit run ui/app.py
pause  
