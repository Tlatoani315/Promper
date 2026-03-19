@echo off
echo ===================================================
echo Instalando Promper en el Inicio de Windows...
echo ===================================================

:: Obtenemos el directorio actual donde esta este script y main.py
set "PROMPER_DIR=%~dp0"
set "PROMPER_SCRIPT=%PROMPER_DIR%main.py"

:: Carpeta de inicio de Windows del usuario actual
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "VBS_FILE=%STARTUP_FOLDER%\RunPromper.vbs"

:: Creamos un script VBScript en la carpeta de inicio.
:: Este VBScript se asegura de correr pythonw (sin consola) y pasando el directorio correcto.
echo Set WshShell = CreateObject("WScript.Shell") > "%VBS_FILE%"
echo ' Ejecutar pythonw para main.py de manera oculta (0) >> "%VBS_FILE%"
echo WshShell.CurrentDirectory = "%PROMPER_DIR%" >> "%VBS_FILE%"
echo WshShell.Run "pythonw.exe """ ^& "%PROMPER_SCRIPT%" ^& """", 0, False >> "%VBS_FILE%"

echo.
echo [Exito] Se ha creado el acceso directo de inicio en:
echo %VBS_FILE%
echo.
echo Promper se ejecutara automaticamente en segundo plano cada vez que enciendas tu computadora.
echo Para probarlo inmediatamente, ejecutaremos el VBScript ahora...
echo.

:: Ejecutarlo ahora para que el usuario no tenga que reiniciar
cscript //nologo "%VBS_FILE%"

echo Promper esta corriendo. Presiona Ctrl + Alt + P en cualquier momento.
pause
