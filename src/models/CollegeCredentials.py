from pydantic import BaseModel

class CollegeCredentials(BaseModel):
    username: str
    password: str