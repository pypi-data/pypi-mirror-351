from sunra_apispec.base.adapter_interface import IElevenLabsAdapter, RequestContentType
from ...sunra_schema import TextToAudioInput
from .schema import (
    ElevenLabsSoundEffectsInput, 
)


class ElevenLabsSoundEffectsAdapter(IElevenLabsAdapter):
    """Adapter for ElevenLabs Sound Effects text-to-audio model."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's TextToAudioInput to ElevenLabs API format."""
        # Validate the input data
        input_model = TextToAudioInput.model_validate(data)
        
        # Create the input for ElevenLabs API
        elevenlabs_input = ElevenLabsSoundEffectsInput(
            text=input_model.prompt,
            duration_seconds=input_model.duration,
            prompt_influence=input_model.prompt_influence
        )
        
        self.request_url = f"https://api.elevenlabs.io/v1/sound-generation?output_format={input_model.output_format}"
        
        return elevenlabs_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_request_content_type(self) -> RequestContentType:
        """Return the content type for the request."""
        return RequestContentType.JSON
    
    def get_request_url(self) -> str:
        """Return the base URL for ElevenLabs API."""
        return self.request_url

    def convert_output(self, data) -> str | list[str]:
        """Convert the ElevenLabs output to audio format expected by Sunra."""
        # ElevenLabs returns binary audio data directly
        return data

    def pick_data_from_output(self, data) -> dict:
        """Pick relevant data from the raw output."""
        return data
