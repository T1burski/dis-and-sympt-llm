from data_modules.db_connection import postgre_connection

def dsa_extrai_dados():
    
    conn, cur = postgre_connection()

    getAll = "SELECT * FROM all_documents"
    
    cur.execute(getAll)
    
    results = cur.fetchall()
    
    allDocuments = []

    for result in results:
        allDocuments.append(result)

    cur.close()
    conn.close()

    return allDocuments
