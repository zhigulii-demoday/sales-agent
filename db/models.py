import datetime
import enum
from typing import List, Optional

from pydantic import BaseConfig, BaseModel, ConfigDict
from sqlalchemy import (Column, Date, DateTime, Float, ForeignKey, Integer,
                        String, Table, Time)
from sqlalchemy import MetaData, text, func
from sqlalchemy.dialects.postgresql import ARRAY, TEXT
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

BaseConfig.arbitrary_types_allowed = True


class Base(DeclarativeBase):
    __allow_unmapped__ = True
    __synchronous__ = False
    __table_args__ = {"schema": "public"}

    def as_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    def short_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    class Config:
        orm_mode = True





class Platform(Base):
    __tablename__ = "platforms"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]]

    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(server_default=func.CURRENT_TIMESTAMP())
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(server_default=func.CURRENT_TIMESTAMP())
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(server_default=text('NULL'))


class Companie(Base):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[Optional[str]]
    description: Mapped[Optional[str]] = mapped_column(TEXT)

    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(server_default=func.CURRENT_TIMESTAMP())
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(server_default=func.CURRENT_TIMESTAMP())
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(server_default=text('NULL'))

class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(primary_key=True)

    platform_id: Mapped[int] = mapped_column(ForeignKey("public.platforms.id"))
    platform: Mapped["Platform"] = relationship()

    platform_uid: Mapped[str] 

    send_initial_message: Mapped[Optional[datetime.datetime]] = mapped_column(server_default=text('NULL'))

    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(server_default=func.CURRENT_TIMESTAMP())
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(server_default=func.CURRENT_TIMESTAMP())
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(server_default=text('NULL'))
