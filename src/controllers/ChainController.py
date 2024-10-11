from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate

from ..helpers import get_settings

import google.generativeai as genai
import logging
import os

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app_settings = get_settings()
genai.configure(api_key=app_settings.GEMINI_API_KEY)


class ChainController:
    def __init__(self):
        # self.embedding_model = HuggingFaceEmbeddings(app_settings.EMBEDDING_MODEL)
        self.embedding_model = HuggingFaceEmbeddings()
        self.gemini_key = app_settings.GEMINI_API_KEY
        self.vector_database_dir = "database"
        self.llm = RunnableLambda(func=self.generate_text)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.transcript = ""

    def generate_text(self, text):
        response = self.model.generate_content(text.text)
        return response.text

    def get_prompt(self):
        prompt = PromptTemplate(
            input_variables=["context", "student_query", "additional_info"],
            template="""
                You are an AI assistant helping university students. Here is a student's question and relevant information to assist them:

                {context}

                Student Question:
                {student_query}
                
                additional information:
                {additional_info}

                Provide a clear, friendly, and natural answer to the student's question based on the context without any further questions.
                The language of the answer will be the same as question.
            """,
        )
        return prompt

    def format_docs(self, docs):
        return "\n\n".join(doc.metadata["responses"] for doc in docs)

    def set_transcript(self, transcript: str):
        self.transcript = transcript

    def add_info(self, docs):
        return self.transcript

    def load_retriever(self):
        if os.path.exists(self.vector_database_dir):
            print("Loading existing Chroma database...")
            vectore_store = Chroma(
                persist_directory=self.vector_database_dir,
                collection_name="local-rag",
                embedding_function=self.embedding_model,
            )
        else:
            print("Chroma database not found. Please create the vector store first.")
            vectore_store = None
        return vectore_store.as_retriever()

    def get_chain(self):
        prompt = self.get_prompt()
        retriever = self.load_retriever()
        return (
            {
                "context": retriever | self.format_docs,
                "student_query": RunnablePassthrough(),
                "additional_info": self.add_info,
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )
