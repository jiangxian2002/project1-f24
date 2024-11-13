import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
load_dotenv()

# Create an engine

# DB credentials
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SERVER = os.getenv("DB_SERVER")
DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"

# Create database engine that connects to the DATABASEURI
engine = create_engine(DATABASEURI)

def runq(q):
        with engine.connect() as conn:
                result = conn.execute(text(q))
                conn.commit()
                return result