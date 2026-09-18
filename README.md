# 🍽️ Chatbot de Comida Peruana

Práctica **Chatbots multimodales** del curso Herramientas de Desarrollo Profesional - TIC (UTP).

Chatbot que responde preguntas sobre la gastronomía del Perú. Está hecho con Python, Streamlit, la librería `openai` y el modelo Whisper.

- **Parte 1:** chat de texto con un modelo de lenguaje (API de chat completions).
- **Parte 2:** pregunta por voz. Se graba con el micrófono o se sube un archivo de audio, Whisper lo transcribe y el chatbot responde.

## ¿Por qué Groq y no la API de OpenAI?

La API de OpenAI es de pago. Groq ofrece una capa gratuita con una API compatible con la de OpenAI, así que el código usa la misma librería `openai` y solo cambia la URL base y la clave. Los modelos usados son:

| Parte | Modelo | Tipo |
|-------|--------|------|
| Chat | `llama-3.3-70b-versatile` | Modelo de lenguaje (Meta Llama 3.3 70B) |
| Voz | `whisper-large-v3-turbo` | Whisper de OpenAI servido por Groq |

La clave se obtiene gratis en <https://console.groq.com/keys>.

## Instalación y ejecución

```bash
git clone https://github.com/USUARIO/chatbot-comida-peruana.git
cd chatbot-comida-peruana
python -m venv .venv
.venv\Scripts\activate        # En Linux o Mac: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env        # Luego pega tu GROQ_API_KEY dentro de .env
streamlit run app.py
```

También se puede pegar la clave directamente en la barra lateral de la aplicación.

## Estructura del proyecto

```
chatbot-comida-peruana/
├── app.py               # Interfaz en Streamlit (chat + entrada por voz)
├── chatbot.py           # Lógica: cliente, respuesta del modelo y transcripción con Whisper
├── requirements.txt     # Dependencias
├── .env.example         # Plantilla de variables de entorno
├── .streamlit/config.toml
├── audio_prueba/        # Audios de ejemplo para probar la Parte 2
└── docs/                # Capturas de la ejecución y el PDF entregable
```

## Cómo funciona

1. `app.py` guarda el historial de la conversación en `st.session_state` y lo dibuja con `st.chat_message`.
2. Cada pregunta se envía a `responder()` en `chatbot.py`, que arma la lista de mensajes (prompt de sistema + historial) y llama a `chat.completions.create` con `stream=True`. La respuesta se muestra en vivo con `st.write_stream`.
3. Para la voz, `st.audio_input` o `st.file_uploader` entregan los bytes del audio. `transcribir()` los envía a `audio.transcriptions.create` con el modelo Whisper y el texto resultante entra al mismo flujo del chat.

## Audios de prueba

Los archivos de `audio_prueba/` se generaron con la voz `es-PE-CamilaNeural` de edge-tts y sirven para probar la transcripción sin micrófono:

- `pregunta_ceviche.mp3`: "Hola, ¿cómo se prepara un ceviche peruano y qué ingredientes necesito?"
- `pregunta_lomo_saltado.mp3`: "¿Cuál es la historia del lomo saltado y de qué región del Perú viene?"
- `pregunta_postres.mp3`: "¿Qué postres típicos me recomiendas probar en Lima?"

## Otros proveedores gratuitos (opcional)

El chat también funciona con cualquier API compatible con OpenAI cambiando las variables del `.env`:

| Proveedor | `LLM_BASE_URL` | `MODELO_CHAT` |
|-----------|----------------|---------------|
| Groq (por defecto) | `https://api.groq.com/openai/v1` | `llama-3.3-70b-versatile` |
| Google Gemini | `https://generativelanguage.googleapis.com/v1beta/openai/` | `gemini-2.5-flash` |
| NVIDIA NIM | `https://integrate.api.nvidia.com/v1` | `meta/llama-3.3-70b-instruct` |

La transcripción con Whisper se mantiene en Groq, ya que Gemini y NVIDIA no exponen Whisper por esta ruta.
