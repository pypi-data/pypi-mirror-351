from typing import Callable
from sunra_apispec.base.adapter_interface import IFalAdapter
from sunra_apispec.base.output_schema import VideoOutput, SunraFile
from ...sunra_schema import ImageToVideoInput
from .schema import FalInput


class FalImageToVideoAdapter(IFalAdapter):
    def convert_input(self, data) -> dict:
        # Validate the input data
        input_model = ImageToVideoInput.model_validate(data)
        
        # Create FalInput instance with mapped values
        fal_input = FalInput(
            prompt=input_model.prompt,
            start_image_url=input_model.start_image,
            end_image_url=input_model.end_image,
            num_frames=input_model.number_of_frames,
            frames_per_second=input_model.frames_per_second,
            resolution=input_model.resolution,
            aspect_ratio=input_model.aspect_ratio,
            num_inference_steps=input_model.number_of_steps,
            guide_scale=input_model.guidance_scale,
            seed=input_model.seed,
            enable_prompt_expansion=input_model.prompt_enhancer,
            acceleration=input_model.acceleration,
        )
        
        # Convert to dict, excluding None values
        return fal_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_fal_model(self) -> str:
        return "fal-ai/wan-flf2v"
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> VideoOutput:
        """Convert FAL output to Sunra VideoOutput format."""
        if isinstance(data, dict) and "video" in data and "url" in data["video"]:
            video_url = data["video"]["url"]
            sunra_file = processURLMiddleware(video_url)
            return VideoOutput(video=sunra_file)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
