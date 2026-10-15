@echo off
rem Risk indicators: Windows Task Scheduler-ийн өдөр тутмын ажил (Airflow-гүй сервер / компьютер).
rem   python ri.py auto --env prod --all : дутуу / алдаатай / өөрчлөгдсөн үзүүлэлтийг л ажиллуулна.
rem Бүртгэх (нэг удаа, cmd-ээс; замыг өөрийнхөөрөө):
rem   schtasks /Create /TN "RiskIndicators" /SC DAILY /ST 07:00 /TR "C:\RA\deploy\windows\ri_auto.cmd"
rem Орчин: RI_ENV хувьсагч (өгөөгүй бол prod). Лог: logs\auto.log + run бүрийн logs\YYYY-MM-DD\<run_id>.log
setlocal
cd /d "%~dp0..\.."
if "%RI_ENV%"=="" set RI_ENV=prod
set PYTHONUTF8=1
".venv\Scripts\python.exe" ri.py auto --env %RI_ENV% --all >> "logs\auto.log" 2>&1
exit /b %ERRORLEVEL%
