import psycopg2

from psycopg2.extras import RealDictCursor

def postgre_connection():

    conn = psycopg2.connect(
        dbname="airflow", 
        user="airflow",    
        password="airflow", 
        host="postgres",    
        port="5432"         
    )

    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    return conn, cur
