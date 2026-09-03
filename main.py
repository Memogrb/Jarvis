import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types
from duckduckgo_search import DDGS

app = FastAPI()

client = genai.Client()

class PromptRequest(BaseModel):
    message: str

def buscar_en_internet(query: str) -> str:
    """Busca información actualizada en la web sobre código, vulnerabilidades o hacking ético."""
    try:
        with DDGS() as ddgs:
            resultados = [r['body'] for r in ddgs.text(query, max_results=3)]
            return "\n".join(resultados) if resultados else "No se encontraron resultados relevantes en la web."
    except Exception as e:
        return f"Error al buscar en internet: {str(e)}"

@app.post("/chat")
def chat_with_jarvis(request: PromptRequest):
    try:
        # Instrucción de sistema avanzada combinando rol técnico y metodología de aprendizaje de Adrià Solà Pastor
        system_instructions = (
            "Eres J.A.R.V.I.S., un asistente virtual avanzado, analítico y eficiente, enfocado "
            "en ser un mentor de élite en Programación (Python, JavaScript, Bash, etc.) y Ciberseguridad / Hacking Ético. "
            "\n\nDIRECTRICES PEDAGÓGICAS (Basadas en el método de aprendizaje acelerado de Adrià Solà Pastor): "
            "1. METAAPRENDIZAJE (El principio del hacha de Abraham Lincoln): Antes de dar una solución masiva de código o hacking, desglosa el tema en: "
            "   - **Conceptos:** Las bases teóricas indispensables. "
            "   - **Hechos:** Principios clave, reglas o restricciones de seguridad. "
            "   - **Procedimientos:** El paso a paso o la estructura práctica. "
            "2. EL PRINCIPIO DE PARETO (20/80): Enfócate en enseñar el 20% de la teoría o sintaxis que genera el 80% de los resultados reales en desarrollo o auditorías de redes. "
            "3. ACCIÓN Y BLOQUES DE FOCO: Recomienda aplicar los conceptos en bloques de trabajo intenso de 90 minutos con descansos, combatiendo la procrastinación con la regla de los 5 minutos cuando el usuario se enfrente a retos complejos. "
            "4. BÚSQUEDA WEB: Si te preguntan por librerías actualizadas, exploits recientes, sintaxis moderna o configuraciones de redes (como iptables, routers, subredes, firewalls), utiliza siempre la herramienta de búsqueda para traer datos reales y precisos. "
            "5. TONO: Profesional, directo, analítico, motivador y sumamente didáctico."
        )

        config = types.GenerateContentConfig(
            system_instruction=system_instructions,
            tools=[buscar_en_internet],
            temperature=0.6,
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
