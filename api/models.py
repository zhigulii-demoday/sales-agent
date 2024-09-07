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

# class platform_post(BaseModel):
#         user_id: int =          Field(
#                                 description="VKid Пользователя"
#                                 )
#         region_id: int =        Field(
#                                 default=78, description="ID Региона (В будущем будет заполняться по JWT, сейчас заполняется автоматически Петербургом)"
#                                 )
#         name: str = Field(
#                                 description="Наименование сервиса/страницы (/pets, /choose_service)"
#                                 )
#         screen_name: str =      Field(
#                                 default="", description="Наименование вкладки внутри сервиса (leisure, map, utility, reference) \n Пустое значение только в Уборке дорог и Сообщениях по ЖКХ, т.к. там нет вкладок"
#                                 )
#         tab_name: str =      Field(
#                                 default="", description="Наименование таба внутри сервиса (места, маршруты в Красивых местах))"
#                                 )                                
#         event_type: str = Field(
#                                 description="Тип действия (type_navgo, phone, button, ad_pop_up)"
#                                 )
#         data: str =             Field(
#                                 default="", description="(Как мы считаем ваш вклад, Все сервисы, Фильтр) При event_type ap_pop_up, ad_modal, button сюда заносится наименование Попапа, Модального окна, Кнопки итд (Если модальное окно, попап берется из https://yazzh-custom.gate.petersburg.ru/ - название должно соответствовать полю category из запроса"
#                                 )
#         utm_campaign: str =     Field(
#                                 default=""
#                                 )
#         utm_source: str =       Field(
#                                 default=""
#                                 )
#         utm_term: str =         Field(
#                                 default=""
#                                 )