from pydantic import BaseModel, Field, ValidationError, validator
from pydantic.functional_validators import AfterValidator
from typing import List, Annotated, Optional




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

class message_post(BaseModel):
    username: str = Field(
            description="Почта или username телеграм"
    )
    text: str = Field(
            description="Текст сообщения"
    )
    chat_type: str = Field(
            description="Типа чата: tg/mail"
    )
    @validator('chat_type')
    def chat_type_validator(cls, v):
            if v not in ['tg', 'mail']:
                    raise ValueError('Supported chat types: "tg", "mail"')
            return v 
    subject: Optional[str] = Field(default=None, description="Тема сообщения")
    message_id: Optional[str] = Field(default=None, description="Идентификатор сообщения")
    
class delete_user(BaseModel):
        username: str = Field(
            description="Почта или username телеграм"
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




class companies_post(BaseModel):
    name: str
    description: str
