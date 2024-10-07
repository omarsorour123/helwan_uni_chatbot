import json
import os
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

class RetrieverController:
    def __init__(self, embedding_model=HuggingFaceEmbeddings(), directory_path='./src/sample_data'):
        self.embedding_model = embedding_model
        self.directory_path = directory_path
        self.retriever = None

    def load_intents(self):
        all_intents = []
        for filename in os.listdir(self.directory_path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.directory_path, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                all_intents.extend(data.get('intents', []))
        return all_intents
    

    def prepare_documents(self,intents):
        documents = []
        for intent in intents:
            for pattern in intent["patterns"]:
                documents.append(Document(page_content=pattern, metadata={"tag": intent["tag"][0], "responses": str(intent["responses"])}))
        return documents
    


    def prepare_retriever(self,documents):

        vectorstore = FAISS.from_documents(documents=documents, embedding=self.embedding_model)
        retriever = vectorstore.as_retriever()

        self.retriever = retriever


    def process(self):
        intents = self.load_intents()

        documents = self.prepare_documents(intents)

        self.prepare_retriever(documents)


        return self.retriever
    


def get_retriever():
    return RetrieverController().process()





