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


from api.models import platform_post, logs_post

from clickhouse_driver import Client

import os
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()
summary_text = 'well'
tag = "Logs"


def log_fix_answer(
        data
):
    res = []
    for row in data[0]:
        _tres = {}
        for i in range(len(data[-1])):
            _tres[data[-1][i][0]] = row[i] 
            if data[-1][i][0] == 'json_data':
                _tres[data[-1][i][0]] = json.loads(_tres[data[-1][i][0]])
        res.append(_tres)
    return res


@router.get("",
            status_code=status.HTTP_200_OK,
            summary=f'{summary_text}',
            tags=[tag])
async def get_quiz_id(
    session: AsyncSession = Depends(get_session),
    platform: Annotated[str, Query()] = 'tg',
    platform_user: Annotated[str, Query()] = '123123'
) -> Any:


    clickhouse = Client(host='213.139.208.158',
                    user=os.environ.get('CLICKHOUSE_USER'),
                    password=os.environ.get('CLICKHOUSE_PASSWORD'),
                    database=os.environ.get('CLICKHOUSE_DB'),
                    secure=False) 
    answer = clickhouse.execute(
            f'''SELECT *
            FROM {os.environ.get('CLICKHOUSE_DB')}.message_logs
            WHERE platform = '{platform}' AND platform_user = '{platform_user}'
            ''',
            with_column_types=True
                        )
    answer = log_fix_answer(answer)

    return {
        'success' : True,
        'status' : 200,
        'data': answer}



@router.post("",
            status_code=status.HTTP_200_OK,
            summary=f'{summary_text}',
            tags=[tag])
async def post_quiz(
    logs_post: logs_post,
    session: AsyncSession = Depends(get_session)
):
    
    data = logs_post.model_dump()
    data['created_at'] = datetime.datetime.now()


    clickhouse = Client(host='213.139.208.158',
                    user=os.environ.get('CLICKHOUSE_USER'),
                    password=os.environ.get('CLICKHOUSE_PASSWORD'),
                    database=os.environ.get('CLICKHOUSE_DB'),
                    secure=False) 
    clickhouse.execute(
            f"INSERT INTO {os.environ.get('CLICKHOUSE_DB')}.message_logs VALUES",
            [(list(data.values()))],
            )

    return {
        'success' : True,
        'status' : 200,
        'data': data}

