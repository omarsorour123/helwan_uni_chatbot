# src/models/ChunkStore.py
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain_chroma import Chroma
from helpers.config import get_settings

import json
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app_settings = get_settings()


class ChunkStore:
    def __init__(self, directory_path):
        self.directory_path = directory_path
        self.all_faqs = []  # Changed variable name for clarity
        self.all_documents = []
        self.embed_model = app_settings.EMBED_MODEL

    def load_data(self, extension):
        for filename in os.listdir(self.directory_path):
            if filename.endswith(extension):
                file_path = os.path.join(self.directory_path, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        data = json.load(file)
                        if isinstance(data, dict):
                            faqs = data.get("faq", [])
                            logger.info(
                                f"Loaded {len(faqs)} categories from {filename}"
                            )
                            self.all_faqs.extend(faqs)
                            logger.info(
                                f"Loaded categories: {self.all_faqs}"
                            )  # Log the loaded faqs
                except json.JSONDecodeError as e:
                    logger.error(f"Error loading JSON from {file_path}: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error when loading {file_path}: {e}")
        logger.info("Data loaded successfully")

    def prepare_documents(self, schema=Document):
        for category in self.all_faqs:
            tag = category.get("علامة")
            questions = category.get("اسألة", [])

            if tag and questions:  # Check if both tag and questions exist
                for q in questions:
                    question_text = q.get("سؤال")
                    answer_text = q.get("اجابة")
                    if question_text and answer_text:
                        self.all_documents.append(
                            schema(
                                page_content=question_text,
                                metadata={
                                    "tag": tag,
                                    "response": answer_text,
                                },
                            )
                        )
                logger.info(
                    f"Processed category: {tag}, total questions: {len(questions)}"
                )
        logger.info(f"Total documents prepared: {len(self.all_documents)}")

    def vector_store(self, embed_model=None):
        if embed_model is None:
            embed_model = HuggingFaceEmbeddings()
        else:
            embed_model = HuggingFaceEmbeddings(self.embed_model)

        # Generate IDs based on the length of documents
        ids = [str(i) for i in range(len(self.all_documents))]

        if not self.all_documents:
            logger.error("No documents to store in the vector store.")
            return None

        vectorstore = Chroma.from_documents(
            documents=self.all_documents,
            embedding=embed_model,
            ids=ids,
            persist_directory="database",
        )
        logger.info("Vector store created successfully.")
        return vectorstore.as_retriever()
