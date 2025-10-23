@echo off
echo Launching COPP AHP Tool on local server...
cd /d "%~dp0"
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
pause
