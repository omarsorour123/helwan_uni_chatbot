"""from fastapi import  FastAPI


app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

"""
from controllers import TranscriptController
from models.CollegeCredentials import CollegeCredentials
# Create an instance of CollegeCredentials
credentials = CollegeCredentials(username='20210605', password='30403252103092')
controller = TranscriptController(credentials=credentials)
print(controller.process())
# trans_controller= TranscriptController



