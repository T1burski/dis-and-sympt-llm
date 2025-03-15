import streamlit as st
from app.elasticSearch import getEsClient, elasticSearch
from app.llm import generate_document_id, query, capture_user_input, capture_user_feedback
from app.evaluation import evaluate

def main():

    st.set_page_config(page_title="AI Symptoms Orientation", page_icon=":100:", layout="wide")

    st.sidebar.title("AI Symptoms Orientation")
    st.sidebar.subheader("Your LLM-oriented medical orientation tool")
    st.sidebar.markdown("---")

    st.title("AI Symptoms Orientation - Describe your symptoms and receive an initial medical orientation")
    st.write("In english, describe in details the symptoms you are experiencing right now.")
    st.write("You will receive a first orientation of the possible disease and the suggested treatment methods.")

    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'docId' not in st.session_state:
        st.session_state.docId = None
    if 'userInput' not in st.session_state:
        st.session_state.userInput = ""
    if 'feedbackSubmitted' not in st.session_state:
        st.session_state.feedbackSubmitted = False

    userInput = st.text_input("Describe your current symptoms:")

    indexName = "elastic_index"

    try:
        esClient = getEsClient()
    except Exception as e:
        print(e)
        st.error("Please wait for the system to get back online. Try again in a couple of minutes.")

    if st.button("Ask"):
        if userInput:
            with st.spinner("Preparing Answer..."):
                try:
                    ragOutputs = elasticSearch(esClient, userInput, indexName)
                    context = "\n\n".join([f"Name of Disease: {output['name']}\nSymptoms: {output['symptoms']}\nTreatment: {output['treatments']}" for output in ragOutputs])

                    evaluateResult = evaluate(lambda q: elasticSearch(esClient, q, indexName))

                    userInput = userInput.replace("'", "").replace('"', "").strip()

                    instructions = "The Question has symptoms of a patient and you are meant to answer both the disease and the treatments for it using simple direct english like a medical expert based on the Context given."

                    prompt = f"""
                    {instructions}

                    Context:
                    {context}

                    Question:
                    {userInput}
                    """

                    try:

                        payload = {
                            "inputs": prompt,
                            "parameters": {
                                "max_new_tokens": 1500,
                                "temperature": 0.2
                            }
                        }
                        
                        result, responseTime = query(payload)

                    except Exception as e:
                        print(f"Error during the usage of the API: {e}")

                    docId = generate_document_id(userInput, result)
                    
                    capture_user_input(
                        docId, 
                        userInput, 
                        result,
                        responseTime,
                        evaluateResult['hit_rate'], 
                        evaluateResult['mrr']
                    )

                    st.session_state.result = result
                    st.session_state.docId = docId
                    st.session_state.userInput = userInput
                    st.session_state.feedbackSubmitted = False

                except Exception as e:
                    print(e)
                    st.error(f"There was an error when processing your request. Please reload the page and try again. Error: {e}")
        else:
            st.warning("Describe your current symptoms to continue.")

    if st.session_state.result:
        st.subheader("Report:")
        st.markdown(st.session_state.result)

        if not st.session_state.feedbackSubmitted:
            st.write("Were you satisfied with the quality of the answer?")
            feedback_col1, feedback_col2 = st.columns(2)
            with feedback_col1:
                if st.button("Satisfied"):
                    capture_user_feedback(st.session_state.docId, st.session_state.userInput, st.session_state.result, True)
                    st.session_state.feedbackSubmitted = True
                    st.success("Feedback given: Satisfied")
            with feedback_col2:
                if st.button("Not Satisfied"):
                    capture_user_feedback(st.session_state.docId, st.session_state.userInput, st.session_state.result, False)
                    st.session_state.feedbackSubmitted = True
                    st.warning("Feedback given: Not Satisfied")

if __name__ == "__main__":
    main()
