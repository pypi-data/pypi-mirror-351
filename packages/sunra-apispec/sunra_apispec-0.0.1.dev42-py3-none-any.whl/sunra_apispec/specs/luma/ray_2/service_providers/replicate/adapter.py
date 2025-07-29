from sunra_apispec.base.adapter_interface import IReplicateAdapter
from ...sunra_schema import TextToVideoInput, ImageToVideoInput
from .schema import Ray2540PInput, Ray2720PInput


class ReplicateTextToVideoAdapter(IReplicateAdapter):
    """Adapter for text-to-video generation using Ray 2 model on Replicate."""
    
    def convert_input(self, data: dict) -> dict:
        """Convert from Sunra's TextToVideoInput to Replicate's input format."""
        # Validate the input data if required
        input_model = TextToVideoInput.model_validate(data)
        
        if input_model.resolution == "720p":
            # Create Input instance with mapped values
            replicate_input = Ray2720PInput(
                prompt=input_model.prompt,
                duration=input_model.duration,
                aspect_ratio=input_model.aspect_ratio,
                loop=input_model.loop,
                concepts=input_model.concepts
            )
            self.model = "luma/ray-2-720p"
        elif input_model.resolution == "540p":
            # Create Input instance with mapped values
            replicate_input = Ray2540PInput(
                prompt=input_model.prompt,
                duration=input_model.duration,
                aspect_ratio=input_model.aspect_ratio,
                loop=input_model.loop,
                concepts=input_model.concepts
            )
            self.model = "luma/ray-2-540p"
        else:
            raise ValueError(f"Invalid resolution {input_model.resolution}")
        
        # Convert to dict, excluding None values
        return replicate_input.model_dump(exclude_none=True, by_alias=True)
    
    # This must be called after convert_input
    def get_replicate_model(self) -> str:
        """Return the Replicate model identifier based on resolution."""
        return self.model

    def convert_output(self, data: dict) -> str | list[str]:
        """Convert Replicate output to Sunra output format."""
        return data


class ReplicateImageToVideoAdapter(IReplicateAdapter):
    """Adapter for image-to-video generation using Ray 2 model on Replicate."""
    
    def convert_input(self, data: dict) -> dict:
        """Convert from Sunra's ImageToVideoInput to Replicate's input format."""
        # Validate the input data
        input_model = ImageToVideoInput.model_validate(data)
        
        if input_model.resolution == "720p":
            # Create Input instance with mapped values
            replicate_input = Ray2720PInput(
                prompt=input_model.prompt,
                start_image_url=input_model.start_image,
                end_image_url=input_model.end_image,
                duration=input_model.duration,
                aspect_ratio=input_model.aspect_ratio,
                loop=input_model.loop,
                concepts=input_model.concepts
            )
            self.model = "luma/ray-2-720p"
        elif input_model.resolution == "540p":
            # Create Input instance with mapped values
            replicate_input = Ray2540PInput(
                prompt=input_model.prompt,
                start_image_url=input_model.start_image,
                end_image_url=input_model.end_image,
                duration=input_model.duration,
                aspect_ratio=input_model.aspect_ratio,
                loop=input_model.loop,
                concepts=input_model.concepts
            )
            self.model = "luma/ray-2-540p"
        else:
            raise ValueError(f"Invalid resolution {input_model.resolution}")
        
        # Convert to dict, excluding None values
        return replicate_input.model_dump(exclude_none=True, by_alias=True)
    
    # This must be called after convert_input
    def get_replicate_model(self) -> str:
        """Return the Replicate model identifier based on resolution."""
        return self.model

    def convert_output(self, data: dict) -> str | list[str]:
        """Convert Replicate output to Sunra output format."""
        return data
