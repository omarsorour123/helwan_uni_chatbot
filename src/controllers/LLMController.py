import asyncio
from functools import lru_cache

from helpers import get_settings
from . import get_retriever

from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableLambda

class LLMController:
    def __init__(self,username = None):
        self.prompt = None
        self.llm = None
        self.rag_chain = None
        self.username = username


    def prepare_prompt(self):
        self.prompt = PromptTemplate(
            input_variables=["context", "student_query"],
            template="""
            You are an AI assistant helping university students. Here is a student's question and relevant information to assist them:

            {context}

            Student Question:
            {student_query}

            Provide a clear, friendly, and natural answer to the student's question based on the context without any further questions.
            """
        )



    def prepare_agent():

        pass 
        #self.llm = agent   

    def prepare_llm(self):
        api_key = get_settings().GEMINI_API_KEY
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0,
            api_key=api_key
        )

        async def generate_text(text):
            try:
                if isinstance(text, tuple):
                    text = text[1]  # Extract the string part if it's a tuple
                # Use the new LLM to generate text
                response = await model.agenerate(text)
                return response.generations[0].text
            except Exception as e:
                print(f"Error generating text: {e}")
                return "I'm sorry, I couldn't generate a response at this time."
            
    
        self.llm = RunnableLambda(func=generate_text)

    @lru_cache(maxsize=100)
    def get_cached_retriever(self):
        return get_retriever()

    def prepare_rag_chain(self):
        retriever = self.get_cached_retriever()
        
        def format_docs(docs):
            return "\n\n".join(doc.metadata['responses'] for doc in docs)
        
        def ensure_string(input_dict):
            return str(self.prompt.format(**input_dict))
        
        self.rag_chain = (
            {
                "context": retriever | RunnableLambda(format_docs), 
                "student_query": RunnablePassthrough()
            }
            | RunnableLambda(ensure_string)
            | self.llm
            | StrOutputParser()
        )

    async def process(self, query):
        self.prepare_llm()
        self.prepare_prompt()
        self.prepare_rag_chain()

        try:
            full_response = await self.rag_chain.ainvoke(query)
            
            
            answer = full_response.strip()              
            return answer
        except Exception as e:
            print(f"Error processing query: {e}")
            return "I'm sorry, I couldn't process your query at this time."