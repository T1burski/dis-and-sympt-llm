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

def extract_sample_evaluation():
    
    conn, cur = postgre_connection()

    getAll = '''SELECT DISTINCT 
                    doc_id, 
                    symptoms
                FROM all_documents 
                LIMIT 200
            '''
    
    cur.execute(getAll)
    
    results = cur.fetchall()
    
    allDocuments = []

    for result in results:
        allDocuments.append(result)

    cur.close()
    conn.close()

    return allDocuments
