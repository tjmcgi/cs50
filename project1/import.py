import os

from sqlalchemy import create_engine

import pandas as pd 
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

data = pd.read_csv("books.csv")

data.to_sql("books", engine, if_exists="replace")
