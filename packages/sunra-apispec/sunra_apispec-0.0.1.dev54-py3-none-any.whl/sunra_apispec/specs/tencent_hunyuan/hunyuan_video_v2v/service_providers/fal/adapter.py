from typing import Callable
from sunra_apispec.base.adapter_interface import IFalAdapter
from sunra_apispec.base.output_schema import VideoOutput, SunraFile
from ...sunra_schema import VideoToVideoInput
from .schema import FalInput


class FalVideoToVideoAdapter(IFalAdapter):
    """Adapter for video-to-video generation using Tencent Hunyuan Video model on FAL."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's VideoToVideoInput to FAL's input format."""
        # Validate the input data
        input_model = VideoToVideoInput.model_validate(data)
        
        # Create FalInput instance with mapped values
        fal_input = FalInput(
            prompt=input_model.prompt,
            video_url=input_model.video,
            # Using default values for the rest of the parameters
            aspect_ratio="16:9",
            resolution="720p",
            strength=0.85,
            enable_safety_checker=False,
        )
        
        # Convert to dict, excluding None values
        return fal_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_fal_model(self) -> str:
        """Return the FAL model identifier."""
        return "fal-ai/hunyuan-video/video-to-video"
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> VideoOutput:
        """Convert FAL output to Sunra VideoOutput format."""
        if isinstance(data, dict) and "video" in data and "url" in data["video"]:
            video_url = data["video"]["url"]
            sunra_file = processURLMiddleware(video_url)
            return VideoOutput(video=sunra_file)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
