from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import ImageOutput, ImagesOutput, SunraFile
from ...sunra_schema import TextToImageInput
from .schema import ReplicateImagen4Input


class ReplicateTextToImageAdapter(IReplicateAdapter):
    """Adapter for text-to-image generation using Imagen4 model on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's TextToImageInput to Replicate's input format."""
        # Validate the input data
        input_model = TextToImageInput.model_validate(data)
        
        # Create Replicate Input instance with mapped values
        replicate_input = ReplicateImagen4Input(
            prompt=input_model.prompt,
            aspect_ratio=input_model.aspect_ratio,
            safety_filter_level="block_only_high"
        )
        
        # Convert to dict, excluding None values
        return replicate_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_replicate_model(self) -> str:
        """Return the Replicate model identifier."""
        return "google/imagen-4"
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> ImagesOutput:
        """Convert Replicate output to Sunra ImagesOutput format."""
        images = []
        if isinstance(data, str):
            # Single image URL
            sunra_file = processURLMiddleware(data)
            images.append(ImageOutput(image=sunra_file))
        elif isinstance(data, list):
            # List of image URLs
            for url in data:
                sunra_file = processURLMiddleware(url)
                images.append(ImageOutput(image=sunra_file))
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
        
        return ImagesOutput(images=images)
