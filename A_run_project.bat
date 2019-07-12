@echo off
cmd /k "cd /d %cd%\boardGUI\venv\Scripts & activate.bat & cd /d  %cd%/boardGUI/ & python manage.py runserver --insecure 0.0.0.0:8000"