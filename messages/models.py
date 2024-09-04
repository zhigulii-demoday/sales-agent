import json
import pydantic
from pydantic import BaseModel

class AnswerModel(BaseModel):
    username: str
    answer: str
    message_id: int | str
    type: str
    

    def __init__(self, username: str, answer: str, message_id: int | str, type: str):
        super().__init__(username=username, answer=answer, type=type, message_id=message_id)
        
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, )
