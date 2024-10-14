# routes/route.py
from fastapi import APIRouter, HTTPException
from langchain_huggingface import HuggingFaceEmbeddings

from pydantic import BaseModel
import os
import logging
import google.generativeai as genai
from langchain_core.runnables import (
    RunnableLambda,
    RunnablePassthrough,
)
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from controllers import LLMController
# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the router
router = APIRouter()

# Google Gemini AI Configuration (Make sure the API key is valid)
genai.configure(api_key="AIzaSyAQSxfrS_rE8uzhCbTXJA9hOAelM2NqXPM")
model = genai.GenerativeModel("gemini-1.5-flash")


# Define the text generation function
def generate_text(text):
    response = model.generate_content(text.text)
    return response.text


# Initialize the LLM & embed model
llm = RunnableLambda(func=generate_text)
embedding_model = HuggingFaceEmbeddings()
directory_path = "database"

# Define the prompt template
prompt = PromptTemplate(
    input_variables=["context", "student_query"],
    template="""
    You are a student at a university. You answer questions based on the following context:

    Context:
    {context}

    Student Question:
    {student_query}

    Provide a clear and helpful answer to the student's question. 
    If the question is about labs, halls, or rooms, only mention the information and nothing else.
    """,
)


# Class for handling input queries
class Query(BaseModel):
    student_query: str


# Function to format the retrieved documents
def format_docs(docs):
    return "\n\n".join(doc.metadata["responses"] for doc in docs)


# Load the Chroma vector store
if os.path.exists(directory_path):
    print("Loading existing Chroma database...")
    vectore_store = Chroma(
        persist_directory=directory_path,
        collection_name="local-rag",
        embedding_function=embedding_model,
    )
else:
    print("Chroma database not found. Please create the vector store first.")
    vectore_store = None


# API route for processing the RAG query
@router.post("/rag_query")
async def rag_query(query: Query):
    
    return {"response": response}
