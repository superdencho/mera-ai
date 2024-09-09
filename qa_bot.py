from langchain.chains import VectorDBQA
from langchain_openai import OpenAI
from pydantic import SecretStr


# Ответ на вопрос на основе индекса
def answer_question(vector_store, question, openai_api_key):
    llm = OpenAI(api_key=openai_api_key)
    qa = VectorDBQA.from_chain_type(llm=llm, vectorstore=vector_store)
    response = qa.run(question)
    if not response:
        return "Извините, я не могу найти ответ на этот вопрос."
    return response
