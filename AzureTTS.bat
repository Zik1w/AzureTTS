@echo off
cd /d %~dp0
SET LOCAL_ROOT=%~dp0

rem change PATHOPATH to your python interpreter location
SET PATHONPATH=py

rem Clear resource folder
if exist %ROOT%TTSAudioFiles RMDIR /S /Q %ROOT%TTSAudioFiles

rem Create resource folder
if not exist %ROOT%TTSAudioFiles md %ROOT%TTSAudioFiles

%PATHONPATH% AzureTTS.py %*
pause

