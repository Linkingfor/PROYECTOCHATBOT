"""
Lógica del chatbot de comida peruana.

Se usa la librería oficial `openai`, pero apuntando a un proveedor gratuito
compatible con la API de OpenAI (Groq). El código es el mismo que se usaría
con OpenAI: solo cambian la URL base y la API key.

Parte 1: responder preguntas con un modelo de lenguaje (chat completions).
Parte 2: transcribir audios con el modelo Whisper (audio transcriptions).
"""
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # carga las variables definidas en el archivo .env

PROVEEDOR = os.getenv("PROVEEDOR", "Groq (capa gratuita)")
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
MODELO_CHAT = os.getenv("MODELO_CHAT", "llama-3.3-70b-versatile")
MODELO_WHISPER = os.getenv("MODELO_WHISPER", "whisper-large-v3-turbo")

PROMPT_SISTEMA = """Eres "Sazón", un asistente experto en gastronomía peruana.
Tu única especialidad es la comida y la bebida del Perú: platos típicos, ingredientes,
recetas paso a paso, historia y origen de los platos, cocina por regiones (costa, sierra
y selva), postres, bebidas como la chicha morada o el pisco sour, y recomendaciones
de qué probar y dónde.

Reglas:
1. Responde siempre en español, con un tono cercano y amable, como un cocinero peruano.
2. Si la pregunta no tiene relación con la comida peruana, explica con amabilidad que
   solo puedes hablar de gastronomía peruana y sugiere una pregunta relacionada.
3. Sé claro y ordenado: usa listas o pasos numerados cuando expliques recetas.
4. No inventes datos. Si no estás seguro de algo, dilo.
5. Mantén las respuestas breves (unas 200 palabras como máximo), salvo que pidan
   una receta completa.
"""


def crear_cliente(api_key: str | None = None) -> OpenAI:
    """Crea el cliente. La key puede venir de la interfaz o del archivo .env."""
    key = api_key or os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError(
            "No se encontró la API key. Escríbela en la barra lateral "
            "o guárdala en el archivo .env como GROQ_API_KEY."
        )
    return OpenAI(api_key=key, base_url=BASE_URL)


def responder(cliente: OpenAI, historial: list[dict]):
    """Parte 1: devuelve la respuesta del modelo como un generador (streaming)."""
    mensajes = [{"role": "system", "content": PROMPT_SISTEMA}] + [
        {"role": m["role"], "content": m["content"]} for m in historial
    ]
    stream = cliente.chat.completions.create(
        model=MODELO_CHAT,
        messages=mensajes,
        temperature=0.7,
        max_tokens=800,
        stream=True,
    )
    for parte in stream:
        if parte.choices and parte.choices[0].delta.content:
            yield parte.choices[0].delta.content


def transcribir(cliente: OpenAI, audio_bytes: bytes, nombre_archivo: str = "audio.wav") -> str:
    """Parte 2: convierte un audio a texto usando el modelo Whisper."""
    resultado = cliente.audio.transcriptions.create(
        model=MODELO_WHISPER,
        file=(nombre_archivo, audio_bytes),
        language="es",
        prompt=(
            "Pregunta sobre comida peruana: ceviche, lomo saltado, ají de gallina, "
            "causa limeña, anticuchos, rocoto relleno, chicha morada, pisco sour."
        ),
        response_format="text",
    )
    texto = resultado if isinstance(resultado, str) else resultado.text
    return texto.strip()
