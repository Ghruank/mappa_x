@echo off
set GROQ_API_KEY=%1
set LLAMA_MODEL_PATH=%2

echo Creating mappa directory in C:\mappa...
mkdir C:\mappa

echo Copying necessary files...
copy "%~dp0mappa.py" C:\mappa\
copy "%~dp0requirements.txt" C:\mappa\

echo Setting up Python virtual environment...
cd C:\mappa
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt

echo Saving environment variables...
setx GROQ_API_KEY "%GROQ_API_KEY%" /M
setx LLAMA_MODEL_PATH "%LLAMA_MODEL_PATH%" /M

echo Creating Windows batch script (mappa.bat)...
(
    echo @echo off
    echo cd /d C:\mappa
    echo call venv\Scripts\activate
    echo python mappa.py
) > C:\mappa\mappa.bat

echo Creating Git Bash script (mappa.sh)...
(
    echo #!/bin/bash
    echo source /c/mappa/venv/Scripts/activate
    echo python /c/mappa/mappa.py
) > C:\mappa\mappa.sh

echo Adding Mappa to system PATH...
setx PATH "%PATH%;C:\mappa" /M

echo Making mappa.sh executable...
bash -c "chmod +x /c/mappa/mappa.sh"

echo Creating a universal 'mappa' command...
(
    echo @echo off
    echo if exist "C:\Program Files\Git\bin\bash.exe" (
    echo     "C:\Program Files\Git\bin\bash.exe" --login -i -c "/c/mappa/mappa.sh"
    echo ) else (
    echo     call C:\mappa\mappa.bat
    echo )
) > C:\mappa\mappa.cmd

echo Adding mappa.cmd as a system-wide command...
doskey mappa=C:\mappa\mappa.cmd

echo Installation Complete! Restart your terminal.
pause