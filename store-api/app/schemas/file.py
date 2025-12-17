from pydantic import BaseModel, ConfigDict

class FileOut(BaseModel):
    path: str
    url: str
    
    model_config = ConfigDict(from_attributes=True)
