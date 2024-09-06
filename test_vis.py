

import asyncio

from db import core
from db import models

from sqlalchemy import text, select

from db.core import PGSession
import pandas as pd
from tqdm import tqdm

import numpy as np 

import os

from dotenv import load_dotenv
load_dotenv()

from autoviz import AutoViz_Class
# import altair as alt


async def main():
    async with PGSession() as session:
        stmt = select(models.Review)
        result = await session.execute(stmt)
        answer = [x.as_dict() for x in result.scalars().all()]
        df = pd.DataFrame.from_records(answer)
        print(df.head())

        AV = AutoViz_Class()

        data = {'col1': [1, 2, 3, 4, 5], 'col2': [5, 4, 3, 2, 1]}
        df = pd.DataFrame(data)

        dft = AV.AutoViz(
            "",
            sep=",",
            depVar="",
            dfte=df,
            header=0,
            verbose=1,
            lowess=False,
            chart_format="server",
            max_rows_analyzed=150000,
            max_cols_analyzed=30,
            save_plot_dir=None
        )

        # chart = alt.Chart(df).mark_point()
        # chart.save('chart.png')
        #print(answer)


if __name__ == '__main__':
    asyncio.run(main())




