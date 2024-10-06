from pydantic import BaseModel
from typing import Literali

class Student(BaseModel):
    name: str
    specialization: str
    total_gpa: float
    grade: str
    hours: int