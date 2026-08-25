@echo off

cd /d C:\JobBot

call venv\Scripts\activate.bat

python job_sources.py >> jobbot.log 2>&1

deactivate