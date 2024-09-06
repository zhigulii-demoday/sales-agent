from pydantic import BaseModel, Field, ValidationError
from pydantic.functional_validators import AfterValidator
from typing import List, Annotated


class platform_post(BaseModel):
        name: str = Field(
                                description="Наименование платформы"
                                )

class platform_get(BaseModel):
        id: int =          Field(
                                description="id"
                                )
        name: str = Field(
                                description="Наименование платформы"
                                )


class logs_post(BaseModel):
        platform: str =          Field(
                                description="tg / mail"
                                )
        platform_user: str = Field(
                                description="tgid / user email"
                                )
        platform_message_id: str = Field(
                                description="message uid"
                                )
        is_user_message: bool = Field(
               description = 'is user message or bots'
        )
        message: str = Field(
               description = 'message text'
        )
#         created_at: bool = Field(
#                description = 'is user message or bots'
#         )


class logs_get(BaseModel):
        platform: str 
        platform_user: str 
        platform_message_id: str 
        is_user_message: bool 
        message: str 
        created_at: bool 