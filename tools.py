import os
import subprocess


def crear_archivo(nombre_archivo: str, contenido: str) -> str:
    """
    Crea un archivo de texto o código en el disco duro del usuario con el contenido especificado.
    Parámetros:
    - nombre_archivo: El nombre del archivo incluyendo su extensión (ej. script.py, notas.txt).
    - contenido: El código o texto que irá dentro del archivo.    
    """
    try:
        ruta_actual = os.getcwd()
        ruta_completa =os.path.join(ruta_actual, nombre_archivo)

        with open(ruta_completa, "w", encoding="utf-8") as f:
            f.write(contenido)

        return f"Éxito: Archivo de sistema '{nombre_archivo}' creado físiscamnete en {ruta_completa}."

    except Exception as e:
        return f"Error de sistema al crear archivo: {str(e)}"

def ejecutar_comando(comando: str) -> str:
    """
    Ejecuta un comando en la terminal de Windows y devuelve el resultado de la consola.
    Útil para revisar configuraciones de red, ping, o estado del sistema.
    Parámetros:
    - comando: El comando exacto a ejecutar (ej. 'ipconfig', 'ping 8.8.8.8', 'dir').
    """
    try:
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True, timeout=15)
        if resultado.returncode == 0:
            return f"Ejecucioón exitosa:\n{resultado.stdout}"
        else:
            return f"Comando falló con error:\n{resultado.stderr}"
    except Exception as e:
        return f"Error al intentar ejecutar: {str(e)}"
    

    