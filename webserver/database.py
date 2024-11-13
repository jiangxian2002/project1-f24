from sqlalchemy import create_engine, text

# Create an engine

# DB credentials
DB_USER = "xj2281"
DB_PASSWORD = "broadwayyy"
DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"
DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"

# Create database engine that connects to the DATABASEURI
engine = create_engine(DATABASEURI)

def runq(q):
        with engine.connect() as conn:
                result = conn.execute(text(q))
                conn.commit()
                return result