# 🍽️ Chatbot de Comida Peruana

Práctica **Chatbots multimodales** del curso Herramientas de Desarrollo Profesional - TIC (UTP).

Chatbot que responde preguntas sobre la gastronomía del Perú. Está hecho con Python, Streamlit, la librería `openai` y el modelo Whisper.

- **Parte 1:** chat de texto con un modelo de lenguaje (API de chat completions).
- **Parte 2:** pregunta por voz. Se graba con el micrófono o se sube un archivo de audio, Whisper lo transcribe y el chatbot responde.

**Integrantes:** Leonardo Martinez Concha y Kevin Julio Chacaltana Vargas.

## ¿Por qué no la API de OpenAI?

La API de OpenAI es de pago. Se buscó una alternativa gratuita que permitiera reutilizar el mismo código visto en clase:

| Parte | Solución | Modelo | Costo |
|-------|----------|--------|-------|
| Chat | Google Gemini expone una API compatible con la de OpenAI, así que se usa la misma librería `openai` cambiando solo la URL base y la clave | `gemini-3.5-flash-lite` | Gratis (capa gratuita de AI Studio) |
| Voz | Whisper corre en la propia computadora con `faster-whisper` (sin clave). El modelo se descarga la primera vez que se usa | Whisper `small` | Gratis |

La clave de Gemini se obtiene en <https://aistudio.google.com/apikey>. La capa gratuita de Gemini tiene un tope de peticiones por día y por modelo (por ejemplo, 20 al día para `gemini-3.5-flash-lite`), suficiente para probar el chatbot. Si se necesita más volumen, Groq ofrece miles de peticiones diarias gratis y el mismo código funciona con solo cambiar el `.env` (ver más abajo). Si se prefiere la ruta por API para Whisper, basta con poner una clave gratuita de Groq en el `.env`.

## Instalación y ejecución

```bash
git clone https://github.com/Linkingfor/PROYECTOCHATBOT.git
cd PROYECTOCHATBOT
python -m venv .venv
.venv\Scripts\activate        # En Linux o Mac: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env        # Luego pega tu GEMINI_API_KEY dentro de .env
streamlit run app.py
```

También se puede pegar la clave directamente en la barra lateral de la aplicación. La primera transcripción tarda un poco más porque descarga el modelo Whisper (unos 480 MB).

## Estructura del proyecto

```
PROYECTOCHATBOT/
├── app.py                 # Interfaz en Streamlit (chat + entrada por voz)
├── chatbot.py             # Lógica: cliente, respuesta del modelo y transcripción con Whisper
├── requirements.txt       # Dependencias
├── .env.example           # Plantilla de variables de entorno
├── .streamlit/config.toml # Tema de la interfaz
├── audio_prueba/          # Audios de ejemplo para probar la Parte 2
└── docs/                  # Capturas de la ejecución y el PDF entregable
```

## Cómo funciona

1. `app.py` guarda el historial de la conversación en `st.session_state` y lo dibuja con `st.chat_message`.
2. Cada pregunta se envía a `responder()` en `chatbot.py`, que arma la lista de mensajes (prompt de sistema + historial) y llama a `chat.completions.create` con `stream=True`. La respuesta se muestra en vivo con `st.write_stream`.
3. Para la voz, `st.audio_input` o `st.file_uploader` entregan los bytes del audio. `transcribir()` los pasa al modelo Whisper con el idioma español y un texto de contexto con nombres de platos. El texto resultante entra al mismo flujo del chat, marcado con un ícono de micrófono.

## Audios de prueba

Los archivos de `audio_prueba/` se generaron con la voz `es-PE-CamilaNeural` de edge-tts y sirven para probar la transcripción sin micrófono:

- `pregunta_ceviche.mp3`: "Hola, ¿cómo se prepara un ceviche peruano y qué ingredientes necesito?"
- `pregunta_lomo_saltado.mp3`: "¿Cuál es la historia del lomo saltado y de qué región del Perú viene?"
- `pregunta_postres.mp3`: "¿Qué postres típicos me recomiendas probar en Lima?"

## Otros proveedores (opcional)

El chat funciona con cualquier API compatible con OpenAI cambiando las variables del `.env`:

| Proveedor | `LLM_BASE_URL` | `MODELO_CHAT` |
|-----------|----------------|---------------|
| Google Gemini (por defecto) | `https://generativelanguage.googleapis.com/v1beta/openai/` | `gemini-3.5-flash-lite` |
| Groq | `https://api.groq.com/openai/v1` | `llama-3.3-70b-versatile` |
| OpenAI | (vacío) | `gpt-4o-mini` |

Si existe `GROQ_API_KEY`, la transcripción deja de hacerse en local y se envía al endpoint `audio.transcriptions` de Groq con el modelo `whisper-large-v3-turbo`.

## Nota sobre certificados SSL

`chatbot.py` activa `truststore` para que Python use los certificados del sistema. Sin esto, en computadoras con antivirus o proxies que inspeccionan HTTPS (por ejemplo Avast) las llamadas a la API y la descarga del modelo fallan con `CERTIFICATE_VERIFY_FAILED`.
