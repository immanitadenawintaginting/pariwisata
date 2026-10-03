@echo off
cd /d %~dp0
.venv\Scripts\streamlit.exe run app\app.py
pause