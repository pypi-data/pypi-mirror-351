"""
Adapter for FLUX.1-Fill-Dev Replicate API service provider.
Converts Sunra schema to Replicate API format.
"""

from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import ImagesOutput, ImageOutput, SunraFile
from ...sunra_schema import ImageToImageInput
from .schema import ReplicateInput, OutputFormatEnum, MegapixelsEnum


class ReplicateImageToImageAdapter(IReplicateAdapter):
    """Adapter for image-to-image generation using FLUX.1-Fill-Dev on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert Sunra ImageToImageInput to Replicate input format."""
        input_model = ImageToImageInput.model_validate(data)
            
        # Map output format
        output_format_mapping = {
            "jpeg": OutputFormatEnum.JPG,
            "png": OutputFormatEnum.PNG
        }
        
        # Map megapixels
        megapixels_mapping = {
            "1": MegapixelsEnum.ONE,
            "0.25": MegapixelsEnum.QUARTER
        }
        
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            image=str(input_model.image),
            mask=str(input_model.mask) if input_model.mask else None,
            num_outputs=input_model.number_of_images,
            num_inference_steps=input_model.number_of_steps,
            guidance=input_model.guidance_scale,
            seed=input_model.seed,
            output_format=output_format_mapping.get(input_model.output_format, OutputFormatEnum.JPG),
            output_quality=80,  # Default quality
            lora_weights=None,  # Default no LoRA
            lora_scale=1.0,  # Default LoRA scale
            disable_safety_checker=False,  # Default safety
            megapixels=megapixels_mapping.get(input_model.megapixels, MegapixelsEnum.ONE)
        )
        
        return replicate_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_replicate_model(self) -> str:
        """Return the Replicate model identifier."""
        return "black-forest-labs/flux-fill-dev" 

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
