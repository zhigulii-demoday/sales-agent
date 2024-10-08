
import asyncio

from db import core
from db import models

from sqlalchemy import text, delete
from sqlalchemy.schema import CreateTable
    
from db.core import PGSession
import pandas as pd
from tqdm import tqdm

import numpy as np 

import os

from dotenv import load_dotenv
load_dotenv()

import json




async def main():
    print(os.environ.get('POSTGRES_DB'))
    async with PGSession() as session:
        await session.execute(text(f"ALTER DATABASE postgres SET SEARCH_PATH TO public;"))
        await session.execute(text(f"CREATE EXTENSION IF NOT EXISTS vector SCHEMA public;"))
        await session.commit()

    print(core.dump_sqlalchemy())
    async with core.pg_engine.begin() as s:

        def metadata_dump(sql, *multiparams, **params):
            print(sql.compile(dialect=s.dialect))

        await s.run_sync(
             models.Base.metadata.create_all
        )
        print('added')


    async with PGSession() as session:

    
        df = pd.read_excel('cleaned_coffee.xlsx')
        df = df.replace(np.nan, None)
        df = df.replace('-', None)

        await session.execute(delete(models.Contact))
        await session.execute(delete(models.Review))
        await session.execute(delete(models.Company))
        await session.execute(delete(models.Platform))


        email_platform = models.Platform(
            name = 'email'
        )
        tg_platform = models.Platform(
            name = 'tg'
        )
        session.add(email_platform)
        session.add(tg_platform)

        company = models.Company(
            name = "tasty_coffee",
            description = "Российская компания, занимающаяся преимущественно обжаркой кофейных зёрен и их продажей. На обжарочных предприятиях используются ростеры компаний Probat и Loring, дожигатели, дестоунеры, промышленные кофемолки Ditting и прочее оборудование."
        )
        session.add(company)

        contact_tg = models.Contact(
            platform = tg_platform,
            platform_uid = 'Faneagain',
            send_initial_message = None,
        )
        session.add(contact_tg)

        contact_email = models.Contact(
            platform = email_platform,
            platform_uid = 'yasha.protasov@gmail.com',
            send_initial_message = None,
        )
        session.add(contact_email)



        for index, row in tqdm(df.iterrows(), total=df.shape[0]):

            new = models.Review(

                company = company,

                product_cat = row['Product Category'],
                product_name = row['Product Name'],

                review_dt = row['Review Date'],
                review_text = row['Review Text'],
                topic = row['Topic'],
                sentiment = row['Sentiment'],
                marketplace = row['Marketplace'],
                embedding = None,
            )
            session.add(new)
        

        await session.commit()




if __name__ == '__main__':
    asyncio.run(main())






        

