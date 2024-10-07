from controllers import LLMController


rag = LLMController()
query = 'i would like to order pasta'
print(rag.process(query))