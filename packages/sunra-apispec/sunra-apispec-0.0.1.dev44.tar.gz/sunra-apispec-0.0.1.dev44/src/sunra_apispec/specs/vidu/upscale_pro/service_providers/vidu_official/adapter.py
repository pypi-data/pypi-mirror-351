"""
Adapter for Vidu Official Upscale Pro API service provider.
Converts Sunra schema to Vidu Official API format.
"""

from sunra_apispec.base.adapter_interface import IViduAdapter
from ...sunra_schema import UpscaleProInput
from .schema import UpscaleProInput as ViduUpscaleProInput


class ViduUpscaleProAdapter(IViduAdapter):
    """Adapter for video upscaling using Vidu Official API."""
    
    def convert_input(self, data: dict) -> dict:
        """Convert Sunra UpscaleProInput to Vidu Official UpscaleProInput format."""
        input_model = UpscaleProInput.model_validate(data)
            
        vidu_input = ViduUpscaleProInput(
            video_url=input_model.video,
            upscale_resolution=input_model.resolution,
        )
            
        return vidu_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_request_url(self) -> str:
        """Get the Vidu Official API endpoint URL for video upscaling."""
        return "https://api.vidu.com/ent/v2/upscale-new"

    def convert_output(self, data: dict) -> str | list[str]:
        """Convert Vidu output to Sunra output format."""
        return data["creations"][0]["url"]
