from helpers import get_settings
from . import get_retriever

from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

import google.generativeai as genai

class LLMController:
    def __init__(self):
        self.prompt = None
        self.llm = None
        self.rag_chain = None

    def prepare_prompt(self):
        self.prompt = PromptTemplate(
            input_variables=["context", "student_query"],
            template="""
            You are a student at a university. You answer questions based on the following context:

            Context:
            {context}

            Student Question:
            {student_query}

            Provide a clear and helpful answer to the student's question.
            """
        )

    def prepare_llm(self):
        api_key = get_settings().GEMINI_API_KEY
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        def generate_text(text):
            if isinstance(text, tuple):
                text = text[1]  # Extract the string part if it's a tuple
            response = model.generate_content(text)
            return response.text
        
        self.llm = RunnableLambda(func=generate_text)

    def prepare_rag_chain(self):
        retriever = get_retriever()
        
        def format_docs(docs):
            return "\n\n".join(doc.metadata['responses'] for doc in docs)
        
        def ensure_string(input_dict):
            return str(self.prompt.format(**input_dict))
        
        self.rag_chain = (
            {
                "context": retriever | RunnableLambda(format_docs), 
                "student_query": RunnablePassthrough()
            }
            | RunnableLambda(ensure_string)  # Convert to string here
            | self.llm
            | StrOutputParser()
        )

    def process(self, query):
        self.prepare_llm()
        self.prepare_prompt()
        self.prepare_rag_chain()

        full_response = self.rag_chain.invoke(query)
        
        # Extract only the answer part
        answer = full_response.split("Provide a clear and helpful answer to the student's question.")[-1].strip()
        return answer