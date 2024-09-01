from decimal import Decimal
from typing import Any, Annotated

import requests

from fastapi import APIRouter, Depends, status, Query, HTTPException, Header, Security, Body
from fastapi.security import APIKeyQuery, HTTPAuthorizationCredentials

from fastapi.responses import ORJSONResponse


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from fastapi.encoders import jsonable_encoder

from db.models import Platform
from db.core import get_session


import datetime
import json
from typing import Literal

from sqlalchemy.orm.attributes import flag_modified


from api.models import platform_post

router = APIRouter()
summary_text = 'well'
tag = "Platforms"


@router.get("",
            status_code=status.HTTP_200_OK,
            summary=f'{summary_text}',
            tags=[tag])
async def get_quiz_id(
    session: AsyncSession = Depends(get_session)
) -> Any:

    stmt = select(Platform)
    result = await session.execute(stmt)
    answer = [x.as_dict() for x in result.scalars().all()]

    if not answer:
        raise HTTPException(status_code=204, detail="Data not found")
    return {
        'success' : True,
        'status' : 200,
        'data': answer}

@router.get("/{id}",
            status_code=status.HTTP_200_OK,
            summary=f'{summary_text}',
            tags=[tag])
async def get_quiz_id(
    id: int,
    session: AsyncSession = Depends(get_session)
) -> Any:

    answer = await session.get(Platform, id)


    if not answer:
        raise HTTPException(status_code=204, detail="Data not found")
    return {
        'success' : True,
        'status' : 200,
        'data': answer.as_dict()}


@router.post("",
            status_code=status.HTTP_200_OK,
            summary=f'{summary_text}',
            tags=[tag])
async def post_quiz(
    platform_post: platform_post,
    session: AsyncSession = Depends(get_session)
):
    
    new = Platform(
        name = platform_post.name
    )
    session.add(new)
    await session.commit()
    await session.refresh(new)

    return {
        'data' : new,
        'success' : True,
        'status' : 200}


