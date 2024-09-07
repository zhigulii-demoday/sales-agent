
import asyncio

from db import core
from db import models

from sqlalchemy import text, delete, select
from sqlalchemy.schema import CreateTable
    
from db.core import PGSession
import pandas as pd
from tqdm import tqdm

import numpy as np 

import os

from dotenv import load_dotenv
load_dotenv()

import json

import datetime


async def main():
    async with PGSession() as session:

        print('Checking contacts to send first message...')
        cts = await session.execute(select(models.Contact))
        for one in cts.scalars():
            if one.send_initial_message == None:
                new_task = models.Task(
                    contact = one,
                    type = 'first_message',
                    status = 'todo',
                    start_after = datetime.datetime.now(),
                    next_schedule_at = datetime.datetime.now(),
                    payload = {'text' : 'text'}
                )
                session.add(new_task)
                one.send_initial_message = datetime.datetime.now()
    
        await session.commit()


        print('Queueing tasks...')
        res = await session.execute(text("""
        WITH locked_tasks AS (SELECT *
                            FROM tasks
                            WHERE (status = 'todo' AND start_after < NOW() AND
                                    scheduler_attempt_count < max_scheduler_attempt_count)
                            LIMIT 1000)
--            updated_rows
--                AS ( UPDATE tasks SET 
--                                    status = 'sent', 
--                                    scheduler_attempt_count = scheduler_attempt_count + 1, 
--                                    next_schedule_at = NOW() + INTERVAL '5 minutes', 
--                                    updated_at = NOW() 
--                                    WHERE id IN (SELECT id FROM locked_tasks))
        SELECT locked_tasks.id, locked_tasks.payload, contacts.platform_uid, platforms."name" 
        FROM locked_tasks
        left join public.contacts on locked_tasks.contact_id = contacts.id
        left join public.platforms on contacts.platform_id = platforms.id;
      
"""))
        for task in res:
            match task.name:
                case 'tg':
                    send = dict(contact=task.platform_uid, data=task.payload)
                    print(send)
                case 'email':
                    send = dict(contact=task.platform_uid, data=task.payload)
                    print(send)




if __name__ == '__main__':
    asyncio.run(main())






        



