import requests
from sunra_apispec.base.adapter_interface import IElevenLabsAdapter, RequestContentType
from ...sunra_schema import AudioToTextInput
from .schema import (
    ElevenLabsScribeV1Input,
)


# Language code mapping from description.md
LANGUAGE_CODE_MAP = {
    "Arabic": "ar",
    "Chinese": "zh",
    "English": "en",
    "French": "fr",
    "German": "de",
    "Hindi": "hi",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Portuguese": "pt",
    "Russian": "ru",
    "Spanish": "es",
    "Turkish": "tr",
    "Bengali": "bn",
    "Dutch": "nl",
    "Indonesian": "id",
    "Persian": "fa",
    "Swahili": "sw",
    "Thai": "th",
    "Vietnamese": "vi"
}


class ElevenLabsScribeV1Adapter(IElevenLabsAdapter):
    """Adapter for ElevenLabs Scribe V1 speech-to-text model."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's AudioToTextInput to ElevenLabs API format."""
        # Validate the input data
        input_model = AudioToTextInput.model_validate(data)
        
        # Get language code from language name if provided
        language_code = LANGUAGE_CODE_MAP.get(input_model.language)
        if not language_code:
            raise ValueError(f"Invalid language: {input_model.language}")

        self.request_url = f"https://api.elevenlabs.io/v1/speech-to-text"

        response = requests.get(input_model.audio)
        audio_data = response.content
        
        return {
            "file": ('audio.mp3', audio_data),
            "model_id": (None, "scribe_v1"),
            "language_code": (None, language_code),
            "tag_audio_events": (None, input_model.tag_audio_events),
            "diarize": (None, input_model.speaker_diarization),
        }
    
    def convert_output(self, data) -> dict:
        """Convert the ElevenLabs output to transcription format expected by Sunra."""
        # ElevenLabs returns transcription data directly
        return {
            "language_code": data["language_code"],
            "language_probability": data["language_probability"],
            "text": data["text"],
            "words": data["words"]
        }
    
    def get_request_content_type(self) -> RequestContentType:
        """Return the content type for the request."""
        return RequestContentType.FORM_DATA
    
    def get_request_url(self) -> str:
        """Return the base URL for ElevenLabs API."""
        return self.request_url
