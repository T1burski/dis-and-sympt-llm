import os
import time
import hashlib
import requests
from app.db_connection import postgre_connection
from datetime import datetime

def generate_document_id(userQuery, answer):

    combined = f"{userQuery[:10]}-{answer[:10]}"
    
    hash_object = hashlib.md5(combined.encode())
    
    hash_hex = hash_object.hexdigest()
    
    document_id = hash_hex[:8]
    
    return document_id

def query(payload):

    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    
    headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_KEY')}"}

    start_time = time.time()

    try:
    
        response = requests.post(API_URL, headers=headers, json=payload)
        
        end_time = time.time()

        responseTime = round(end_time - start_time, 2)

        final_response_json = response.json()

        final_response = final_response_json[0]["generated_text"] \
                        .replace(payload["inputs"], "") \
                        .replace("'", "") \
                        .replace('"', "") \
                        .replace("\n", " ") \
                        .replace("\t", " ") \
                        .replace("\\", "") \
                        .strip()
        
        answer_start = final_response.find("Answer: ")
        if answer_start != -1:
            final_response = final_response[answer_start + len("Answer: "):].strip()
        
        return final_response, responseTime
    
    except Exception as e:
        print(f"Error: {e}")
        raise Exception(f"Error: {e}")

def capture_user_input(docId, userQuery, result, responseTime, hit_rate, mrr):

    conn, cur = postgre_connection()
    
    try:
        create = """
            CREATE TABLE sys_evaluation (
                id SERIAL PRIMARY KEY,
                doc_id VARCHAR(10) NOT NULL,
                user_input TEXT NOT NULL,
                result TEXT NOT NULL,
                response_time DOUBLE PRECISION NOT NULL,
                hit_rate_score DOUBLE PRECISION NOT NULL,
                mrr_score DOUBLE PRECISION NOT NULL,
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        cur.execute(create)

    except Exception as e:
        print(e)
        conn.rollback() 

    try:

        sql = f"""
            INSERT INTO sys_evaluation
            (doc_id, user_input, result, response_time, hit_rate_score, mrr_score)
            VALUES
            ('{docId}', '{userQuery}', '{result}', {responseTime}, {hit_rate}, {mrr})
        """

        cur.execute(sql)

    except Exception as e:

        print(e)
        conn.rollback() 

    conn.commit()
    cur.close()
    conn.close()

    return "System evaluation data inserted succesfully"

def capture_user_feedback(docId, userQuery, result, feedback):

    conn, cur = postgre_connection()
    
    try:

        create = """
            CREATE TABLE user_feedback (
                id SERIAL PRIMARY KEY,
                doc_id VARCHAR(10) NOT NULL,
                user_input TEXT NOT NULL,
                result TEXT NOT NULL,
                is_satisfied BOOLEAN NOT NULL,
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """

        cur.execute(create)

    except Exception as e:
        print(e)
        conn.rollback() 

    try:
        sql = f"""
            INSERT INTO user_feedback
            (doc_id, user_input, result, is_satisfied)
            VALUES
            ('{docId}', '{userQuery}', '{result}', {feedback})
        """
        cur.execute(sql)

    except Exception as e:
        print(e)
        conn.rollback() 

    conn.commit()
    cur.close()
    conn.close()

    return "User feedback data inserted succesfully"
