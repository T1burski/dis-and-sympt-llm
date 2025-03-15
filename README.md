# Diseases and Symptoms: An AI Medical Orientation System

![image](https://github.com/user-attachments/assets/98736e89-201f-4f81-b673-ef52341f326c)

### 1) Project's Goal:
This project focuses on building a system that provides, for both patient and doctors, an assistant to interpret the symptoms that a patient has, providing a first orientation on the possible disease and the respective treatment. Obs: This does not serve as a medical professional, but only as a first orientation on cause and treatment, specially in cases that symptoms are too complex and overlap across different medical conditions.


### 2) Strategy and Tools Used:
The assistant is built on a LLM and RAG system to provide the answer to the patient's informed symptoms, returning a well written and direct answer. Here, we are dealing with people's health. Therefore, we need total control on the interpretation of the user's input and on the tool's output. So, the LLM receives a context on the diseases, symptoms and treatments, and the LLM will provide the answers based on this context.
