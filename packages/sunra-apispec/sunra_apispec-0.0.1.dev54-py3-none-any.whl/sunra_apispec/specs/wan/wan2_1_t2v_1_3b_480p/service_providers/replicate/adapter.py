from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import VideoOutput, SunraFile
from ...sunra_schema import TextToVideoInput
from .schema import ReplicateInput


class ReplicateTextToVideoAdapter(IReplicateAdapter):
    def convert_input(self, data) -> dict:
        # Validate the input data if required
        input_model = TextToVideoInput.model_validate(data)
        
        # Create ReplicateInput instance with mapped values
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            seed=input_model.seed,
            frame_num=input_model.number_of_frames,
            sample_steps=input_model.number_of_steps,
            sample_guide_scale=input_model.guidance_scale,
            aspect_ratio=input_model.aspect_ratio,
        )
        
        # Convert to dict, excluding None values
        return replicate_input.model_dump(exclude_none=True, by_alias=True) 
    
    def get_replicate_model(self) -> str:
        return "wan-video/wan-2.1-1.3b"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> VideoOutput:
        """Convert Replicate output to Sunra VideoOutput format."""
        if isinstance(data, str):
            # Single video URL
            sunra_file = processURLMiddleware(data)
            return VideoOutput(video=sunra_file)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
