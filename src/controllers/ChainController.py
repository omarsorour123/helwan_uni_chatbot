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
        try:
            logger.info("Initializing ChainController...")
            self.embedding_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-mpnet-base-v2"
            )
            self.gemini_key = app_settings.GEMINI_API_KEY
            self.vector_database_dir = "database"
            self.llm = RunnableLambda(func=self.generate_text)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            self.transcript = ""
            logger.info("ChainController initialized successfully.")
        except Exception as e:
            logger.exception("Failed to initialize ChainController.")
            raise RuntimeError("Initialization error") from e

    def generate_text(self, text):
        try:
            logger.info("Generating text...")
            response = self.model.generate_content(text.text)
            logger.info("Text generation completed.")
            return response.text
        except Exception as e:
            logger.exception("Failed to generate text.")
            raise RuntimeError("Text generation error") from e

    def get_prompt(self):
        try:
            logger.info("Creating prompt template...")
            prompt = PromptTemplate(
                input_variables=["context", "student_query", "additional_info"],
                template="""
                    You are an AI assistant helping university students. Here is a student's question and relevant information to assist them:

                    context:
                    {context}

                    Student Question:
                    {student_query}

                    additional information:
                    {additional_info}

                    Provide a clear, friendly, and natural answer to the student's question based on the context without any further questions.
                    The language of the answer will be the same as question.
                """,
            )
            logger.info("Prompt template created successfully.")
            return prompt
        except Exception as e:
            logger.exception("Failed to create prompt template.")
            raise RuntimeError("Prompt creation error") from e

    def format_docs(self, docs):
        try:
            logger.info("Formatting documents...")
            formatted_docs = "\n\n".join(doc.metadata["responses"] for doc in docs)
            logger.info("Document formatting completed.")
            return formatted_docs
        except Exception as e:
            logger.exception("Failed to format documents.")
            raise RuntimeError("Document formatting error") from e

    def set_transcript(self, transcript: str):
        logger.info("Setting transcript...")
        self.transcript = transcript
        logger.info("Transcript set successfully.")

    def add_info(self, docs):
        logger.info("Adding additional info...")
        return self.transcript

    def load_retriever(self):
        try:
            logger.info("Loading retriever...")
            if os.path.exists(self.vector_database_dir):
                logger.info("Loading existing Chroma database...")
                vectore_store = Chroma(
                    persist_directory=self.vector_database_dir,
                    embedding_function=self.embedding_model,
                )
                logger.info("Chroma database loaded successfully.")
            else:
                logger.error(
                    "Chroma database not found. Please create the vector store first."
                )
                raise FileNotFoundError("Vector store not found.")
            return vectore_store.as_retriever()
        except Exception as e:
            logger.exception("Failed to load retriever.")
            raise RuntimeError("Retriever loading error") from e

    def get_chain(self):
        try:
            logger.info("Constructing chain...")
            prompt = self.get_prompt()
            retriever = self.load_retriever()
            chain = (
                {
                    "context": retriever | self.format_docs,
                    "student_query": RunnablePassthrough(),
                    "additional_info": self.add_info,
                }
                | prompt
                | self.llm
                | StrOutputParser()
            )
            logger.info("Chain construction completed successfully.")
            return chain
        except Exception as e:
            logger.exception("Failed to construct the chain.")
            raise RuntimeError("Chain construction error") from e
