@echo off


:: Start ComfyUI in the background
echo Starting ComfyUI...
start "" C:\Users\yudhi\Desktop\ComfyUI_windows_portable\start_comfyui.bat

:: Wait for ComfyUI to initialize (1 minute)
echo Waiting for ComfyUI to initialize...
timeout /t 30

echo ComfyUI should be ready now. Checking...
curl -s -o nul -w "ComfyUI HTTP Status: %%{http_code}\n" http://127.0.0.1:8188/

:: Activate your virtual environment
echo Activating virtual environment...
call C:\Users\yudhi\Desktop\__Projects__\ComfyUI_Deploy\venv\Scripts\activate.bat

:: Run your Python script
echo Running Python script...
python C:\Users\yudhi\Desktop\__Projects__\ComfyUI_Deploy\relight_workflow.py

:: Optionally, you can add a command to stop ComfyUI after your script finishes

:: Keep the window open to see any output or errors
pause