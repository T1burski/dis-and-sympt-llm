import os 
import hashlib
import pandas as pd
from elasticsearch import Elasticsearch
from data_modules.db_connection import postgre_connection
from data_modules.data_extraction import dsa_extrai_dados


def generate_document_id(doc):


    combined = f"{doc['name'][:5]}-{doc['symptoms']}-{doc['treatments']}"
    

    hash_object = hashlib.md5(combined.encode())
    

    hash_hex = hash_object.hexdigest()
    

    document_id = hash_hex[:8]
    

    return document_id


def create_table():

    conn, cur = postgre_connection()
    
    try:

        create = """
            CREATE TABLE all_documents (
                doc_id VARCHAR(10),
                name TEXT NOT NULL,
                symptoms TEXT NOT NULL,
                treatments TEXT NOT NULL
            );
        """

        cur.execute(create)

    except Exception as e:

        print(e)

        try:

            create = """
                TRUNCATE TABLE all_documents;
            """
            cur.execute(create)

        except Exception as e:
            print(e)

    conn.commit()
    cur.close()
    conn.close()

def insert_csv_data():

    conn, cur = postgre_connection()

    allData = []

    try:
        all_data = pd.read_csv(f"{os.getcwd()}/dags/data/Diseases_Symptoms.csv")
    
    except Exception as e:
        print(f"An error occured when extracting the data from csv file: {e}")

    for _ , row in all_data.iterrows():

        data = {
            "name": str(row['Name']).replace("'", "").replace('"', "").strip(),
            "symptoms": str(row['Symptoms']).replace("'", "").replace('"', "").strip(),
            "treatments": str(row['Treatments']).replace("'", "").replace('"', "").strip()
        }

        docId = generate_document_id(data)

        allData.append((str(docId), data['name'], data['symptoms'], data['treatments']))

    try:

        overwrite = """
                TRUNCATE TABLE all_documents;
                """
        cur.execute(overwrite)
        
        args = ','.join(cur.mogrify("(%s,%s,%s,%s)", i).decode('utf-8') for i in allData)
        insert_query = "INSERT INTO all_documents (doc_id, name, symptoms, treatments) VALUES" + (args)
                
        cur.execute(insert_query)

        conn.commit()
        print("Data inserted successfuly.")

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

    return "Data from CSV inserted succesfully."

def create_index():

    esClient = Elasticsearch("http://elasticsearch:9200")

    indexName = "elastic_index"
    
    indexSettings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "name": {"type": "text"},
                "symptoms": {"type": "text"},
                "treatments": {"type": "text"}
            }
        }
    }

    if esClient.indices.exists(index=indexName):
        esClient.indices.delete(index=indexName)
    
    try:
        esClient.indices.create(index=indexName, body=indexSettings)
    
    except Exception as e:
        print(f"error when creating index: {e}")

    data = dsa_extrai_dados()

    for doc in data:
        try:
            print("================")
            print("Data Added:")
            print(f"{doc}")
            print("================")
            esClient.index(index=indexName, document=doc)
        
        except Exception as e:
            print(f"error when adding data to index: {e}")
            print(f"error doc: {doc}")

    return "Data loaded to index succesfully."
