@echo off
color 0B
title Universal Audio Studio - Setup
cls
echo ========================================================
echo      INSTALLATION UNIVERSELLE (V2.34)
echo ========================================================
echo.
echo [1] NVIDIA (GeForce RTX/GTX) - Mode CUDA
echo [2] AMD / INTEL / CPU - Mode DirectML
echo.
set /p choice="Choix (1 ou 2) : "
if "%choice%"=="1" goto NVIDIA
if "%choice%"=="2" goto STANDARD
goto END

:NVIDIA
cls
echo Installation NVIDIA...
py -3.10 -m pip uninstall -y onnxruntime onnxruntime-directml onnxruntime-gpu audio-separator
py -3.10 -m pip install "audio-separator[gpu]==0.29.0"
py -3.10 -m pip install -r requirements.txt
goto SUCCESS

:STANDARD
cls
echo Installation STANDARD...
py -3.10 -m pip uninstall -y onnxruntime onnxruntime-directml onnxruntime-gpu audio-separator
py -3.10 -m pip install "audio-separator[cpu]==0.29.0"
py -3.10 -m pip install onnxruntime-directml
py -3.10 -m pip install -r requirements.txt
goto SUCCESS

:SUCCESS
echo TERMINE ! Lancez LANCER_STUDIO.bat
pause
exit
:END
pause
