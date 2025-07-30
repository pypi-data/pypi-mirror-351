# Custom configuration schemas
from pydantic import BaseModel

# Example configuration - replace with your actual schemas
class ExampleConfig(BaseModel):
    setting1: str = "default"
    setting2: int = 42
