"""
Adapter for Vidu Official Vidu2.0 API service provider.
Converts Sunra schema to Vidu Official API format.
"""

from sunra_apispec.base.adapter_interface import IViduAdapter
from ...sunra_schema import ImageToVideoInput, ReferenceImagesToVideoInput
from .schema import (
    ViduImageToVideoInput, 
    ViduReferenceImagesToVideoInput,
    ViduStartEndToVideoInput,
    ModelEnum,
)


class ViduImageToVideoAdapter(IViduAdapter):
    """Adapter for image-to-video generation using Vidu Official API."""
    
    def convert_input(self, data: dict) -> dict:
        """Convert Sunra ImageToVideoInput to Vidu Official ImageToVideoInput or StartEndToVideoInput format."""
        input_model = ImageToVideoInput.model_validate(data)
            
        # Check if both start_image and end_image are provided
        if input_model.start_image and input_model.end_image:
            # Use StartEndToVideoInput format
            vidu_input = ViduStartEndToVideoInput(
                model=ModelEnum.VIDU2_0.value,
                prompt=input_model.prompt,
                images=[str(input_model.start_image), str(input_model.end_image)],
                duration=input_model.duration,
                resolution=input_model.resolution,
                seed=input_model.seed,
                movement_amplitude=input_model.movement_amplitude,
            )
        else:
            # Use ImageToVideoInput format
            vidu_input = ViduImageToVideoInput(
                model=ModelEnum.VIDU2_0.value,
                prompt=input_model.prompt,
                images=[str(input_model.start_image)],
                duration=input_model.duration,
                resolution=input_model.resolution,
                movement_amplitude=input_model.movement_amplitude,
                seed=input_model.seed,
            )
            
        return vidu_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_request_url(self) -> str:
        """Get the Vidu Official API endpoint URL for image-to-video."""
        return "https://api.vidu.com/ent/v2/imgToVideo"

    def convert_output(self, data: dict) -> str | list[str]:
        """Convert Vidu output to Sunra output format."""
        return data["creations"][0]["url"]
    

class ViduReferenceImagesToVideoAdapter(IViduAdapter):
    """Adapter for reference-images-to-video generation using Vidu Official API."""
    
    def convert_input(self, data: dict) -> dict:
        """Convert Sunra ReferenceImagesToVideoInput to Vidu Official ReferenceImagesToVideoInput format."""
        input_model = ReferenceImagesToVideoInput.model_validate(data)
            
        vidu_input = ViduReferenceImagesToVideoInput(
            model=ModelEnum.VIDU2_0.value,
            prompt=input_model.prompt,
            images=[str(img) for img in input_model.reference_images],
            duration=input_model.duration,
            aspect_ratio=input_model.aspect_ratio,
            resolution=input_model.resolution,
            movement_amplitude=input_model.movement_amplitude,
            seed=input_model.seed,
        )
        
        return vidu_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_request_url(self) -> str:
        """Get the Vidu Official API endpoint URL for reference-images-to-video."""
        return "https://api.vidu.com/ent/v2/referenceToVideo" 

    def convert_output(self, data: dict) -> str | list[str]:
        """Convert Vidu output to Sunra output format."""
        return data["creations"][0]["url"]
