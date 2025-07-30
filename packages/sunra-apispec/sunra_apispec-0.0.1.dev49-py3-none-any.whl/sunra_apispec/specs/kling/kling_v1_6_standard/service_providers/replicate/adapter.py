from sunra_apispec.base.adapter_interface import IReplicateAdapter
from ...sunra_schema import TextToVideoInput, ImageToVideoInput, ReferenceImagesToVideoInput
from .schema import ReplicateInput


class ReplicateTextToVideoAdapter(IReplicateAdapter):
    """Adapter for text-to-video generation using Kling v1.6 Standard model on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's TextToVideoInput to Replicate's input format."""
        # Validate the input data if required
        input_model = TextToVideoInput.model_validate(data)
        
        # Create ReplicateInput instance with mapped values
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            negative_prompt=input_model.negative_prompt or "",
            cfg_scale=input_model.guidance_scale,
            aspect_ratio=input_model.aspect_ratio,
            duration=input_model.duration
        )
        
        # Convert to dict, excluding None values
        return replicate_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_replicate_model(self) -> str:
        """Return the Replicate model identifier."""
        return "kwaivgi/kling-v1.6-standard"

    def convert_output(self, data) -> str | list[str]:
        """Convert Replicate output to Sunra output format."""
        return data


class ReplicateImageToVideoAdapter(IReplicateAdapter):
    """Adapter for image-to-video generation using Kling v1.6 Standard model on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's ImageToVideoInput to Replicate's input format."""
        # Validate the input data if required
        input_model = ImageToVideoInput.model_validate(data)
        
        # Create ReplicateInput instance with mapped values
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            negative_prompt=input_model.negative_prompt or "",
            cfg_scale=input_model.guidance_scale,
            start_image=input_model.start_image,
            aspect_ratio=input_model.aspect_ratio,
            duration=input_model.duration
        )
        
        # Convert to dict, excluding None values
        return replicate_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_replicate_model(self) -> str:
        """Return the Replicate model identifier."""
        return "kwaivgi/kling-v1.6-standard"

    def convert_output(self, data) -> str | list[str]:
        """Convert Replicate output to Sunra output format."""
        return data


class ReplicateReferenceImagesToVideoAdapter(IReplicateAdapter):
    """Adapter for reference-images-to-video generation using Kling v1.6 Standard model on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's ReferenceImagesToVideoInput to Replicate's input format."""
        # Validate the input data if required
        input_model = ReferenceImagesToVideoInput.model_validate(data)
        
        # Create ReplicateInput instance with mapped values
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            negative_prompt=input_model.negative_prompt or "",
            cfg_scale=input_model.guidance_scale,
            reference_images=input_model.reference_images,
            aspect_ratio=input_model.aspect_ratio,
            duration=input_model.duration
        )
        
        # Convert to dict, excluding None values
        return replicate_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_replicate_model(self) -> str:
        """Return the Replicate model identifier."""
        return "kwaivgi/kling-v1.6-standard"

    def convert_output(self, data) -> str | list[str]:
        """Convert Replicate output to Sunra output format."""
        return data
