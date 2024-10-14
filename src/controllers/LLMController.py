from helpers import get_settings
from . import get_retriever

from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain.tools import Tool
from langchain.agents import AgentType, initialize_agent

import json
import os

class LLMController:
    def __init__(self):
        self.prompt = None
        self.llm = None
        self.rag_chain = None
        self.username = '20210605'

    def prepare_prompt(self):
        self.prompt = PromptTemplate(
            input_variables=["context", "student_query"],
            template="""
            You are an AI assistant helping university students. Here is a student's question and relevant information to assist them:

            {context}

            Student Question:
            {student_query}

            Provide a clear, friendly, and natural answer to the student's question based on the context without any further questions or asking for information about him.
            """
        )

    def prepare_llm(self):
        api_key = get_settings().GEMINI_API_KEY
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0,
            api_key=api_key
        )

        def generate_text(text):
            if isinstance(text, tuple):
                text = text[1]  # Extract the string part if it's a tuple
            response = model.invoke(text)
            return response.text
        
        self.llm = model

    def prepare_agent(self):
        def get_student_data(input=""):
            """
            return student data and courses
            """
            base_folder = r'json'
            student_json = self.username + '.json'
            json_path = os.path.join(base_folder, student_json)
            with open(json_path, 'r', encoding='utf-8') as file:
                data = json.load(file)   

            return json.dumps(data)
        
        get_student_informations = Tool(
            name="GradeTool",
            func=get_student_data,
            description="Invoke this tool when a student asks for something related to his courses or grades or informations or gpa"
        )   
        
        self.llm = initialize_agent(
            tools=[get_student_informations],
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

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
            | RunnableLambda(lambda x: x['output'])  # Ensure the output is a string
            | StrOutputParser()
        )

    def process(self, query):
        self.prepare_llm()
        self.prepare_agent()
        self.prepare_prompt()
        self.prepare_rag_chain()

        full_response = self.rag_chain.invoke(query)
        
        # Extract only the answer part
        answer = full_response.split("Provide a clear and helpful answer to the student's question.")[-1].strip()
        return answer