Promper es un sistema rapido para la gestion de promps personales de forma rapida

Con un simple comando (Ctrl + Alt + P) se puede acceder a una interfaz para gestionar los promps

Los promps se guardan en una base de datos local (SQLite) y se pueden exportar a un archivo JSON


Las mejores tecnologías para "Promper"
Lenguaje: Python.

Interfaz Gráfica (UI): Tkinter (viene nativo con Python, es ligero y perfecto para una ventana minimalista tipo bloc de notas) o PyQt si quieres que se vea más moderno.

Atajos de teclado globales: La librería keyboard.

Gestión del portapapeles: La librería pyperclip.


## Cómo ejecutar Promper en segundo plano (Background)

Para que Promper se ejecute de forma silenciosa y se quede escuchando el atajo `Ctrl + Alt + P` sin mostrar una ventana de consola negra todo el tiempo:

**En Windows:**
1. Abre tu terminal o consola de comandos.
2. Navega hasta la carpeta del proyecto.
3. Ejecuta el archivo usando `pythonw` en lugar de `python`:
   ```bash
   pythonw main.py
   ```
Al usar `pythonw`, el script se ejecutará sin abrir la ventana de Command Prompt, quedando activo en la bandeja de procesos en segundo plano.

Para que inicie automáticamente con Windows:
Crea un acceso directo del archivo `main.py` y colócalo en la carpeta de inicio de Windows (`Win + R`, escribe `shell:startup`). En las propiedades del acceso directo, puedes asegurar que ejecute `pythonw.exe` en lugar de `python.exe`.
