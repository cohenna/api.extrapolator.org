# filepath: /home/nick/dev/extrapolator/api.extrapolator.org/create_db.py
import os
from sqlmodel import SQLModel, create_engine
from extrapolation import Extrapolation  # make sure your module name is correct

DATABASE_URL = os.getenv("DATABASE_URL")#, "mysql+mysqlconnector://extrapolator:extrapolator@localhost/extrapolator")
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    print("Database and tables created.")

if __name__ == "__main__":
    create_db_and_tables()