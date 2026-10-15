import os 
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

import database
import tools


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("No se encontró la variable GEMINI_API_KEY en el archivo .env")

client = genai.Client(api_key=api_key)
app = FastAPI(title="JARVIS Core", version="1.0")

database.init_db()

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def index():
    return {"system": "JARVIS Core API status: ONLINE"}

@app.post("/api/chat")
def chat(request: ChatRequest):
    try:
        database.save_message("user", request.message)

        historial_db = database.get_history(limit=10)
        contexto_conversacion = "Historial:\n"
        for rol, contenido in historial_db:
            contexto_conversacion += f"{rol}: {contenido}\n"
        prompt_final = contexto_conversacion + f"\nuser: {request.message}"

        instrucciones_maestro = """
        Eres JARVIS, un asistente de Inteligencia Artificial avanzado, investigador multidisciplinario y docente de nivel experto.

        Cuando el usuario te pida investigar, explicar o enseñarle sobre cualquier tema, debes regirte bajo las siguientes directivas:

        1. Rol de Experto Absoluto: Adopta inmediatamente la postura de un especialista senior en el dominio solicitado (ingeniería, ciencia, historia, arquitectura de sistemas, etc.).
        2. Análisis y Cobertura Extensa: Evita las respuestas superficiales. Desglosa la información desde sus principios fundamentales hasta sus aplicaciones avanzadas y casos de uso reales.
        3. Metodología Pedagógica Paso a Paso:
           - Divide el tema en módulos o etapas lógicas.
           - Explica el 'por qué' teórico antes de pasar a la práctica.
           - Muestra ejemplos concretos, código, diagramas de flujo o comandos según aplique.
           - Verifica la comprensión antes de dar saltos de complejidad.
        4. Autonomía Operativa: Si la explicación requiere crear archivos de código de ejemplo o ejecutar diagnósticos en el sistema del usuario, utiliza tus herramientas locales (`crear_archivo`, `ejecutar_comando`) de forma proactiva.
        5. Tono Profesional y Preciso: Mantén una comunicación clara, directa, con alto nivel técnico y sin relleno innecesario.
        """
                
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt_final,
            config=types.GenerateContentConfig(
                system_instruction=instrucciones_maestro,
                tools=[tools.crear_archivo, tools.ejecutar_comando],
                temperature=0.3,
            )
        )

        respuesta_final = ""

        if response.function_calls:
            for function_call in response.function_calls:
                nombre_funcion = function_call.name
                argumentos = function_call.args

                if nombre_funcion == "crear_archivo":
                    print(f"JARVIS ejecutando: {nombre_funcion} con {argumentos}")
                    resultado_ejecucion = tools.crear_archivo(argumentos["nombre_archivo"], argumentos["contenido"])                        
                    respuesta_final = f"Ejecuté la acción. Resultado local: {resultado_ejecucion}\n\n"

                elif nombre_funcion == "ejecutar_comando":
                    print(f"JARVIS ejecutando: {nombre_funcion} -> {argumentos['comando']}")
                    resultado_ejecucion = tools.ejecutar_comando(argumentos["comando"])
                    respuesta_fianal += f"Comando ejecutando en consola. Resultado:\n{resultado_ejecucion}\n\n" 

                if response.text:
                        respuesta_final += response.text
        else:
            respuesta_final = response.text

        database.save_message("jarvis", respuesta_final)


        return {"reply": respuesta_final}
    
    except Exception as e:
        error_msg = str(e)
        if "503" in error_msg or "UNAVAILABLE" in error_msg:
            return {
                "reply": "JARVIS: Mis servidores cognitivos están saturados en este momento debido a alta demanda. Por favor, dame unos minutos y vuelve a intentarlo. "
            }
        
        raise HTTPException(status_code=500, detail=error_msg)
