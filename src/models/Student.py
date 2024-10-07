from pydantic import BaseModel

class Student(BaseModel):
    name: str
    specialization: str
    total_gpa: float
    grade: str
    hours: int
    student_id: str

    def __init__(self, **data):

        data['name'] = data['name'].lower()
        super().__init__(**data)