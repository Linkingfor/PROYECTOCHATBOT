"""
Lógica del chatbot de comida peruana.

Parte 1: responder preguntas con un modelo de lenguaje usando la librería oficial
`openai`. Por defecto se conecta a Google Gemini (capa gratuita), que expone una API
compatible con la de OpenAI: el código es el mismo, solo cambian la URL base y la clave.

Parte 2: transcribir audios con el modelo Whisper. Por defecto Whisper corre en la
propia computadora (faster-whisper, sin clave). Si existe GROQ_API_KEY, se usa el
endpoint de transcripciones de Groq, idéntico al de OpenAI.
"""
import io
import os
from functools import lru_cache

from dotenv import load_dotenv
from openai import OpenAI

try:  # Usa los certificados del sistema; evita errores SSL con antivirus o proxies
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

load_dotenv()  # carga las variables definidas en el archivo .env

# ----- Parte 1: proveedor del modelo de lenguaje (API compatible con OpenAI) -----
NOMBRE_PROVEEDOR = os.getenv("PROVEEDOR", "Google Gemini (capa gratuita)")
BASE_URL = os.getenv("LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
MODELO_CHAT = os.getenv("MODELO_CHAT", "gemini-3.5-flash-lite")
VARIABLES_CLAVE = ("LLM_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY", "OPENAI_API_KEY")

# ----- Parte 2: Whisper -----
WHISPER_LOCAL = os.getenv("WHISPER_LOCAL", "small")  # tiny, base, small, medium o large-v3
WHISPER_API = os.getenv("MODELO_WHISPER", "whisper-large-v3-turbo")
USAR_WHISPER_API = bool(os.getenv("GROQ_API_KEY"))
MODELO_WHISPER = f"{WHISPER_API} (API de Groq)" if USAR_WHISPER_API else f"Whisper {WHISPER_LOCAL} (local)"
VOCABULARIO = (
    "Pregunta sobre comida peruana: ceviche, lomo saltado, ají de gallina, "
    "causa limeña, anticuchos, rocoto relleno, chicha morada, pisco sour."
)

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
    """Crea el cliente. La clave puede venir de la interfaz o del archivo .env."""
    key = api_key or next((os.getenv(v) for v in VARIABLES_CLAVE if os.getenv(v)), None)
    if not key:
        raise ValueError(
            "No se encontró la API key. Escríbela en la barra lateral "
            "o guárdala en el archivo .env (por ejemplo GEMINI_API_KEY)."
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
        max_tokens=2000,
        stream=True,
    )
    for parte in stream:
        if parte.choices and parte.choices[0].delta.content:
            yield parte.choices[0].delta.content


@lru_cache(maxsize=1)
def _cargar_whisper():
    """Carga el modelo Whisper local una sola vez (la primera vez lo descarga)."""
    from faster_whisper import WhisperModel

    return WhisperModel(WHISPER_LOCAL, device="cpu", compute_type="int8")


def transcribir(audio_bytes: bytes, nombre_archivo: str = "audio.wav") -> str:
    """Parte 2: convierte un audio a texto usando el modelo Whisper."""
    if USAR_WHISPER_API:
        cliente = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
        resultado = cliente.audio.transcriptions.create(
            model=WHISPER_API,
            file=(nombre_archivo, audio_bytes),
            language="es",
            prompt=VOCABULARIO,
            response_format="text",
        )
        texto = resultado if isinstance(resultado, str) else resultado.text
        return texto.strip()

    segmentos, _ = _cargar_whisper().transcribe(
        io.BytesIO(audio_bytes), language="es", beam_size=5, initial_prompt=VOCABULARIO
    )
    return " ".join(segmento.text.strip() for segmento in segmentos)
