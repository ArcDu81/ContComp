import os
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver

load_dotenv()

SUPABASE_URI = os.getenv("SUPABASE_POSTGRES_URL")

# Reduced max_size to 5 to respect free-tier limits and added a timeout
connection_pool = ConnectionPool(
    conninfo=SUPABASE_URI,
    max_size=5,
    kwargs={
        "autocommit": True, 
        "prepare_threshold": 0,
        "connect_timeout": 10
    }
)

def get_checkpointer():
    checkpointer = PostgresSaver(connection_pool)
    checkpointer.setup() 
    return checkpointer