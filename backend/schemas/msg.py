from pydantic import BaseModel

 
class Msg(BaseModel):
    """Generic message schema for simple API responses."""
    msg: str 