# Diseases and Symptoms: An AI Medical Orientation System

![image](https://github.com/user-attachments/assets/98736e89-201f-4f81-b673-ef52341f326c)

### 1) Project's Goal:
This project focuses on building a system that provides, for both patient and doctors, an assistant to interpret the symptoms that a patient has, providing a first orientation on the possible disease and the respective treatment. Obs: This does not serve as a medical professional, but only as a first orientation on cause and treatment, specially in cases that symptoms are too complex and overlap across different medical conditions.


### 2) Strategy and Tools Used:
The assistant is built on a LLM and RAG system to provide the answer to the patient's informed symptoms, returning a well written and direct answer. Here, we are dealing with people's health. Therefore, we need total control on the interpretation of the user's input and on the tool's output. So, the LLM receives a context on the diseases, symptoms and treatments, and the LLM will provide the answers based on this context.

In order to guarantee a robust project, every module and sub-system was containerized using Docker, using a shared network through Docker Compose. The simplified diagram in the start of this readme file represents the architecture chosen. In practice, three containers were built and connected to each other:

### airflow:
Provides the airflow webserver, scheduler and other functionalities to orchestrate the extraction and load of the context data to the Elastic Search database. Image was built on customized Dockerfile. Example of the airflows UI showing the status of each DAG run:

![image](https://github.com/user-attachments/assets/8994448f-d69f-4499-bd61-47591bee01bd)

### elasticsearch:
Provides the Elastic Search database with the indexed data that feeds the RAG context system. Image built on available official image of Elastic Search 8.15.1.

### app:
Provides the streamlit webapp, building the front-end and the connection between the system and the LLM API using HuggingFace. Image was built on customized Dockerfile.

The PostgreSQL database that is part of airflow was used, for simplicity reasons, to store data such as the context data (the data that was loaded to Elastic Search) and two other tables: one that stores the performance metrics of the RAG system (response time, hit_rate_score and mmr_score) and one that stores user feedbacks.
Modularization was applied to make the project organized, facilitating maintenance.

### 3) AI: The LLM and RAG Approaches:
The LLM used was the Mistral AI's Mistral-7B-Instruct-v0.2. And for the storage of the context data used in the RAG approach, Elastic Search database was used, as mentioned before.

LLM specs: Since we are dealing with a sensible theme (people's health and lives) two important parameters were set: We want lengthy responses, so the LLM can have the necessary space to develop the critical answer and not leave any space for ambiguity, therefore, we set max_new_tokens to 1500. The theme here is sensible and there is no space for creativity and pretty storytelling: temperature param is set to a low value, 0.2.

RAG specs: There are three fields in the context data:

### i) Name of the Disease
### ii) Symptoms
### iii) Treatment

The user will add in the query text related to the symptoms, and the LLM needs to output potential diseases names and their respective treatments. Therefore, the RAG system searches the Elastic Search database for the symptoms (given in the user's query) and returns the top 4 ("size" was set to 4 here) records from the database which will feed the context. 

In order to track the performance of the RAG system (how well Elastic Search is proividing good and correct context based on input query), two common metrics were used:

### Hit Rate:
This metric assesses how well the search mecanism works in returning the desired record by measuring the desired outcome's frequency of appearence in the top-N results. It is calculated by:

### Number of hits / Total number of queries

Where the number of hits is the number of queries in which the desired answer was present (each query can have multiple answers bwing returned. In our case, 4 results in each query).

### MRR (Mean Reciprocal Rank):
Used to evaluate the retrieval component of the system’s performance in retrieving pertinent documents that facilitate the development of accurate and pertinent responses in the context of Retrieval-Augmented development (RAG). This metric checks the position of the correct answer in the list returned by Elastic Search and calculates the reciprocal mean of the position/rank in every search event used in addressing the performance. It is calculated by:

![image](https://github.com/user-attachments/assets/4cde22f7-2a40-499e-b269-fd8e25004c33)

In order to build the payload sent to the LLM API (HuggingFace), the following strategy of prompt-building was used:

### full_payload = instructions + Context + Question

Where:

-- instructions contains a fixed strategy for the LLM to behave ("The Question has symptoms of a patient and you are meant to answer both the disease and the treatments for it using simple direct english like a medical expert based on the Context given.")

-- Context contains the outputs of the RAG system.

-- Question contains the user's query/input


### 4) The Web App (Front-End):
The Web App was built using Streamlit.

When the user accesses the page, they see the following:

![image](https://github.com/user-attachments/assets/b9afa2cd-8267-4db9-bce0-5e9686803b9d)

When the user types their symptoms and clicks on 'Ask', the system returns the output and the user can give their feedback.

![image](https://github.com/user-attachments/assets/87052be6-c358-40ed-81a2-2c3c1ff6c63f)

When the feedback is given, a message is displayed stating that the user gave their opinion.

![image](https://github.com/user-attachments/assets/141abc33-f928-4fef-b154-e9b3490ca413)

Everytime the user Asks something and gives a feedback, all the generated data is recorded in the PostgreSQL database.

### sys_evaluation table (records response time, hit rate and mrr scores)
![image](https://github.com/user-attachments/assets/d48f0179-cf2a-4a6d-a556-be687fa6cccc)

### user_feedback table (records user's feedback)
![image](https://github.com/user-attachments/assets/e821ee11-85ef-4ce4-b905-99afcdbb8d72)


### 5) Conclusions, Running the Project & Improvements for the Future:
