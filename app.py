"""
Chatbot de Comida Peruana - interfaz en Streamlit.

Parte 1: chat de texto con un modelo de lenguaje.
Parte 2: preguntas por voz (micrófono o archivo) transcritas con Whisper.
"""
import streamlit as st

from chatbot import (
    MODELO_CHAT,
    MODELO_WHISPER,
    NOMBRE_PROVEEDOR,
    crear_cliente,
    responder,
    transcribir,
)

st.set_page_config(page_title="Chatbot de Comida Peruana", page_icon="🍽️")

BIENVENIDA = (
    "¡Hola! Soy **Sazón**, tu guía de comida peruana. "
    "Pregúntame por platos, ingredientes, recetas, historia o qué comer en cada región del Perú."
)

# ---------- Estado de la sesión (historial de la conversación) ----------
if "mensajes" not in st.session_state:
    st.session_state.mensajes = [{"role": "assistant", "content": BIENVENIDA}]


def reiniciar_chat():
    st.session_state.mensajes = [{"role": "assistant", "content": BIENVENIDA}]


# ---------- Barra lateral: configuración y entrada por voz ----------
with st.sidebar:
    st.header("⚙️ Configuración")
    api_key = st.text_input(
        "API key (opcional si está en .env)",
        type="password",
        help="La clave de Gemini se obtiene gratis en https://aistudio.google.com/apikey",
    )
    st.caption(f"Proveedor: {NOMBRE_PROVEEDOR}")
    st.caption(f"Modelo de chat: `{MODELO_CHAT}`")
    st.caption(f"Modelo de voz: `{MODELO_WHISPER}`")
    st.button("🗑️ Nueva conversación", on_click=reiniciar_chat)

    st.divider()
    st.header("🎤 Parte 2: pregunta por voz")
    grabacion = st.audio_input("Graba tu pregunta")
    archivo = st.file_uploader(
        "...o sube un archivo de audio",
        type=["mp3", "wav", "m4a", "ogg", "webm", "flac"],
    )
    boton_transcribir = st.button("📝 Transcribir con Whisper y enviar")

# ---------- Zona principal: el chat ----------
st.title("🍽️ Chatbot de Comida Peruana")
st.caption("Práctica: Chatbots multimodales · Python + Streamlit + modelo de lenguaje + Whisper")

for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        prefijo = "🎤 " if mensaje.get("por_voz") else ""
        st.markdown(prefijo + mensaje["content"])


def enviar(texto: str, por_voz: bool = False):
    """Agrega la pregunta al historial, consulta al modelo y muestra la respuesta."""
    st.session_state.mensajes.append({"role": "user", "content": texto, "por_voz": por_voz})
    with st.chat_message("user"):
        st.markdown(("🎤 " if por_voz else "") + texto)

    with st.chat_message("assistant"):
        try:
            cliente = crear_cliente(api_key)
            info = {}
            respuesta = st.write_stream(responder(cliente, st.session_state.mensajes, info))
            if info.get("modelo") and info["modelo"] != MODELO_CHAT:
                st.caption(f"Respondió el modelo de respaldo `{info['modelo']}` (cuota del principal agotada).")
        except Exception as error:
            respuesta = f"⚠️ No pude responder: {error}"
            st.error(respuesta)
    st.session_state.mensajes.append({"role": "assistant", "content": respuesta})


# Parte 2: audio -> Whisper -> texto -> chatbot
if boton_transcribir:
    audio = grabacion or archivo
    if audio is None:
        st.sidebar.warning("Primero graba o sube un audio.")
    else:
        with st.spinner("Transcribiendo con Whisper (la primera vez carga el modelo)..."):
            try:
                texto = transcribir(audio.getvalue(), audio.name)
            except Exception as error:
                texto = ""
                st.sidebar.error(f"No pude transcribir: {error}")
        if texto:
            st.sidebar.success(f"Transcripción: {texto}")
            enviar(texto, por_voz=True)

# Parte 1: texto escrito
if pregunta := st.chat_input("Escribe tu pregunta sobre comida peruana..."):
    enviar(pregunta)
