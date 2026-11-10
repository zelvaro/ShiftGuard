"""Transcription des notes vocales (darija, français, arabe) via un modèle Whisper."""

from app.core.config import get_settings


async def transcribe(audio: bytes, filename: str = "voice.ogg") -> str:
    s = get_settings()
    # TODO : appeler l'API du fournisseur choisi (Groq / OpenAI) avec s.stt_model.
    # Garder cette fonction comme unique point d'entrée pour pouvoir changer de fournisseur.
    raise NotImplementedError(f"Transcription non branchée (provider={s.llm_provider})")
