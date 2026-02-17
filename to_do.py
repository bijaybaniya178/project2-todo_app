import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
import os


load_dotenv()
host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
username = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
port = os.getenv("DB_PORT")


try:
    
    with psycopg.connect(
        host=host,
        dbname=db_name,
        user=username,
        password=db_password,
        port=port ) as conn:
        with conn.cursor(row_factory=dict_row) as curr:
             create_table_query="""
                CREATE TABLE IF NOT EXISTS user_tasks(
                    Id SERIAL PRIMARY KEY,  
                    Username VARCHAR(50) NOT NULL,
                    Task VARCHAR(255) NOT NULL ,
                    Status BOOLEAN DEFAULT FALSE,
                    CreatedAt TIMESTAMP DEFAULT NOW()
                    );
                """
             curr.execute(create_table_query)
             #print(host, db_name, username, port)
             
             insert_data="""
             INSERT INTO user_tasks (username,task )
             VALUES(%s ,%s)"""
             a=("bijay","Learn dsa and computer network")
             curr.execute(insert_data,a)

        
             
            
except Exception as v:
    print("Database Error Occur",v)

