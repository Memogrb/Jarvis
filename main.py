import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types
from duckduckgo_search import DDGS  # Nota: asegúrate de usar duckduckgo_search tal cual

app = FastAPI()

# Inicializa el cliente de Gemini (tomará la API key de las variables de entorno de la nube)
client = genai.Client()

class PromptRequest(BaseModel):
    message: str

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
        config = types.GenerateContentConfig(
            system_instruction=(
                "Eres JARVIS, un asistente virtual avanzado, analítico y eficiente. "
                "Responde de manera concisa y profesional. Si necesitas datos actuales, "
                "noticias o información en tiempo real que desconozcas, utiliza la herramienta de búsqueda."
            ),
            tools=[buscar_en_internet],
            temperature=0.7,
        )

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=request.message,
            config=config,
        )

        return {"response": response.text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)