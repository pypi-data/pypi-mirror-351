from typing import Callable
from sunra_apispec.base.adapter_interface import IFalAdapter
from sunra_apispec.base.output_schema import VideoOutput, SunraFile
from ...sunra_schema import PikascenesInput
from .schema import FalInput, PikaImage


class FalPikascenesAdapter(IFalAdapter):
    """Adapter for Pikascenes video generation using Pika 2.2 model on FAL."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's PikascenesInput to FAL's input format."""
        # Validate the input data
        input_model = PikascenesInput.model_validate(data)
        
        # Convert image items to the format expected by FAL
        pika_images = [ PikaImage(image_url=img) for img in input_model.images ]
        
        # Create FalInput instance with mapped values
        fal_input = FalInput(
            prompt=input_model.prompt,
            images=pika_images,
            aspect_ratio=input_model.aspect_ratio,
            resolution=input_model.resolution,
            ingredients_mode=input_model.ingredients_mode,
        )
        
        # Convert to dict, excluding None values
        return fal_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_fal_model(self) -> str:
        """Return the FAL model identifier."""
        return "fal-ai/pika/v2.2/pikascenes"
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> VideoOutput:
        """Convert FAL output to Sunra VideoOutput format."""
        if isinstance(data, dict) and "video" in data and "url" in data["video"]:
            video_url = data["video"]["url"]
            sunra_file = processURLMiddleware(video_url)
            return VideoOutput(video=sunra_file)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
