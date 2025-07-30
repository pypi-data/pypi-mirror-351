from enum import Enum


class RequestContentType(Enum):
    JSON = "application/json"
    FORM_DATA = "multipart/form-data"
    URL_ENCODED = "application/x-www-form-urlencoded"
    TEXT = "text/plain"
    BINARY = "application/octet-stream"
    

class ServiceProviderEnum(Enum):
    FAL = "fal"
    REPLICATE = "replicate"
    MINIMAX = "minimax"
    BLACK_FOREST_LABS = "black_forest_labs"
    VIDU = "vidu"
    VOLCENGINE = "volcengine"
    OPENAI = "openai"
    ELEVENLABS = "elevenlabs"


class IFalAdapter:
    def __init__(self):
       pass

    def convert_input(self, data) -> dict:
        pass

    def convert_output(self, data) -> str | list[str]:
        pass
    
    def get_fal_model(self) -> str:
        pass

    def pick_data_from_output(self, data) -> dict:
        pass


class IReplicateAdapter:
    def __init__(self):
        pass

    def convert_input(self, data) -> dict:
        pass

    def convert_output(self, data) -> str | list[str]:
        pass
    
    def get_replicate_model(self) -> str:
        pass

    def pick_data_from_output(self, data) -> dict:
        pass


class IMinimaxAdapter:
    def __init__(self):
        pass

    def convert_input(self, data) -> dict:
        pass

    def convert_output(self, data) -> str | list[str]:
        pass

    def get_request_url(self) -> str:
        pass

    def get_status_url(self, task_id: str) -> str:
        pass

    def get_file_url(self, file_id: str) -> str:
        pass

    def pick_data_from_output(self, data) -> dict:
        pass


class IBlackForestLabsAdapter:
    def __init__(self):
        pass

    def convert_input(self, data) -> dict:
        pass

    def convert_output(self, data) -> str | list[str]:
        pass

    def get_bfl_model(self) -> str:
        pass

    def pick_data_from_output(self, data) -> dict:
        pass


class IViduAdapter:
    def __init__(self):
        pass

    def convert_input(self, data) -> dict:
        pass

    def convert_output(self, data) -> str | list[str]:
        pass
    
    def get_request_url(self) -> str:
        pass

    def pick_data_from_output(self, data) -> dict:
        pass


class IVolcengineAdapter:
    def __init__(self):
        pass
    
    def convert_input(self, data) -> dict:
        pass
    
    def convert_output(self, data) -> str | list[str]:
        pass

    def get_request_url(self) -> str:
        pass

    def get_status_url(self, task_id: str) -> str:
        pass

    def pick_data_from_output(self, data) -> dict:
        pass


class IOpenAIAdapter:
    def __init__(self):
        pass
    
    def convert_input(self, data) -> dict:
        pass
    
    def convert_output(self, data) -> str | list[str]:
        pass

    def get_request_url(self) -> str:
        pass
    
    def get_api_key(self) -> str:
        pass

    def pick_data_from_output(self, data) -> dict:
        pass


class IElevenLabsAdapter:
    def __init__(self):
        pass
    
    def convert_input(self, data) -> dict:
        pass
    
    def convert_output(self, data) -> str | list[str]:
        pass

    def get_request_content_type(self) -> RequestContentType:
        pass

    def get_request_url(self) -> str:
        pass

    def pick_data_from_output(self, data) -> dict:
        pass


BaseAdapter = (
    IFalAdapter
    | IReplicateAdapter
    | IMinimaxAdapter
    | IBlackForestLabsAdapter
    | IViduAdapter
    | IVolcengineAdapter
    | IOpenAIAdapter
    | IElevenLabsAdapter
)
