from sqlalchemy import create_engine, MetaData
from sqlalchemy.schema import CreateTable
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
import asyncio
import logging
import os

from dotenv import load_dotenv
import json
load_dotenv()

logging.info('Using url for PG - ', os.environ.get('PG_URL'))

pg_engine = create_async_engine(f'postgresql+asyncpg://' +
                                os.environ.get('POSTGRES_USER') + ':' + 
                                os.environ.get('POSTGRES_PASSWORD') + '@' + 
                                'localhost' + ':' +
                                '5432/' + os.environ.get('POSTGRES_DB'))

PGSession: async_sessionmaker = async_sessionmaker(pg_engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncSession:
    async with PGSession() as session:
        yield session

def dump_sqlalchemy():
    """ Returns the entire content of a database as lists of dicts"""
    engine = create_engine(f'postgresql://' +
                                os.environ.get('POSTGRES_USER') + ':' + 
                                os.environ.get('POSTGRES_PASSWORD') + '@' + 
                                'localhost' + ':' +
                                '5432/' + os.environ.get('POSTGRES_DB'))    
    meta = MetaData()
    meta.reflect(bind=engine) 
    result = ""
    with engine.connect() as conn:
        for table in meta.sorted_tables:
            result += str(CreateTable(table)) + '\n'
    return result