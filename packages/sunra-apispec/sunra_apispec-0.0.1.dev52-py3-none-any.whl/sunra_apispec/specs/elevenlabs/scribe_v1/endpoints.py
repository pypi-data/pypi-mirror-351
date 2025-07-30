import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import AudioToTextInput, TranscriptionOutput
from .service_providers.elevenlabs_official.adapter import ElevenLabsScribeV1Adapter

model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="ElevenLabs Scribe V1 API",
    description="API for ElevenLabs Scribe V1 audio-to-text transcription",
    version="1.0",
    output_schema=TranscriptionOutput,
)

@service.app.post(
    f"/{model_path}/audio-to-text",
    response_model=SubmitResponse,
    description="Transcribe audio to text using ElevenLabs Scribe V1 model",
)
def audio_to_text(body: AudioToTextInput) -> SubmitResponse:
    pass


registry_items = {
    f"{model_path}/audio-to-text": [
        {
            "service_provider": ServiceProviderEnum.ELEVENLABS.value,
            "adapter": ElevenLabsScribeV1Adapter,
            "request_type": RequestType.SYNC,
        }
    ]
}
