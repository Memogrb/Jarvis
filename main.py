import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types
from duckduckgo_search import DDGS
from supabase import create_client, Client

app = FastAPI()

# Configuración de clientes (Gemini y Supabase)
client = genai.Client()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class PromptRequest(BaseModel):
    message: str
    session_id: str = "default_user"  # Permite identificar tu sesión o dispositivo

def buscar_en_internet(query: str) -> str:
    """Busca información actualizada en la web."""
    try:
        with DDGS() as ddgs:
            resultados = [r['body'] for r in ddgs.text(query, max_results=3)]
            return "\n".join(resultados) if resultados else "No se encontraron resultados relevantes."
    except Exception as e:
        return f"Error al buscar en internet: {str(e)}"

@app.post("/chat")
def chat_with_jarvis(request: PromptRequest):
    try:
        # 1. Recuperar el historial reciente de Supabase (últimos 10 mensajes para mantener contexto)
        history_response = supabase.table("jarvis_memory") \
            .select("role, content") \
            .eq("session_id", request.session_id) \
            .order("created_at", desc=False) \
            .limit(10) \
            .execute()
        
        db_history = history_response.data if history_response.data else []

        # 2. Construir el historial compatible con Gemini SDK
        formatted_contents = []
        for row in db_history:
            formatted_contents.append(
                types.Content(
                    role=row["role"],
                    parts=[types.Part.from_text(text=row["content"])]
                )
            )
        
        # Añadir el mensaje actual del usuario al flujo
        formatted_contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=request.message)]
            )
        )

        # 3. Instrucción de sistema con rol de mentor experto y continuidad
        system_instructions = (
            "Eres J.A.R.V.I.S., un asistente virtual avanzado y mentor de élite en Programación y Ciberseguridad / Hacking Ético. "
            "Mantienes una memoria estricta del progreso con el usuario. Si te pregunta en qué se quedaron o qué deben repasar, "
            "revisa el historial de la conversación para retomar exactamente el último punto, ejercicio o duda planteada. "
            "Utiliza el método de aprendizaje acelerado (metaaprendizaje, regla 20/80 de Pareto) y busca en internet si requieres datos técnicos actuales."
        )

        config = types.GenerateContentConfig(
            system_instruction=system_instructions,
            tools=[buscar_en_internet],
            temperature=0.6,
        )

        # 4. Generar respuesta con el contexto histórico completo
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=formatted_contents,
            config=config,
        )

        respuesta_ia = response.text

        # 5. Guardar la interacción actual en la base de datos de Supabase
        supabase.table("jarvis_memory").insert([
            {"session_id": request.session_id, "role": "user", "content": request.message},
            {"session_id": request.session_id, "role": "model", "content": respuesta_ia}
        ]).execute()

        return {"response": respuesta_ia}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
