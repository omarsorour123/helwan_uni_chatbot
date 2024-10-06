from models import CollegeCredentials
import requests
import os


class TranscriptController:
    

    def __init__(self,credentials:CollegeCredentials) -> None:
        self.username = credentials.username
        self.password = credentials.password

        
    