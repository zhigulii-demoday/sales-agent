
import asyncio

from db import core
from db import models



async def main():
    async with core.pg_engine.begin() as s:
        print('adding_new_tables...')
        await s.run_sync(
             models.Base.metadata.create_all
        )
        print('added')

if __name__ == '__main__':
    asyncio.run(main())






        

