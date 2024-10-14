import google.generativeai as genai
import os
import shutil
from helpers.config import Settings, get_settings
from .DownloadTranscriptController import DownloadTranscriptController
import json
from models import CollegeCredentials,Student



settings = get_settings()
class TranscriptController: 
    FULL_HOURS = [6, 6, 63, 9, 39, 21]

    def __init__(self,credentials: CollegeCredentials) -> None:
        
        self.credentials = credentials
        self.json_directory = "json"
        self.ensure_json_directory()

    def ensure_json_directory(self):
        if not os.path.exists(self.json_directory):
            os.makedirs(self.json_directory)

    def process(self):


        self.transcript_path = DownloadTranscriptController(credentials=self.credentials).process()

        content = self.extract_information_from_pdf()

        content , student = self.extract_student_information(content)

        content = self.add_remaining_hours(content)

        full_transcript ={
            'student_info': student.model_dump_json(),

            'courses':content
        }
        temp_path =f'{student.student_id}.json' 
        with open(temp_path, 'wb') as f:
            f.write(json.dumps(full_transcript).encode('utf-8'))
        final_path = os.path.join(self.json_directory, os.path.basename(temp_path))
        shutil.move(temp_path, final_path)
        print(f"Transcript moved to {final_path}")
                    
        return content , student

    def extract_information_from_pdf(self):

        key = settings.GEMINI_API_KEY
        genai.configure(api_key=key)


        model = genai.GenerativeModel('gemini-1.5-pro')
        file_ref = genai.upload_file(self.transcript_path)

        prompt = settings.EXTRACT_STUDENT_INFORMATION_PROMPT
        response = model.generate_content(
        [file_ref, prompt],
        generation_config = genai.types.GenerationConfig(
        temperature=0,
        )

            )
        
        return response.text
    
    def extract_student_information(self,information):
        content = json.loads(information)
        student = Student(
            name = content['student_name'],
            student_id = str(content['student_id']),
            specialization = content['specialization'],
            hours = content['hours'],
            grade = content['grade'],
            total_gpa = content['total_gpa'],
        )


        del content['student_name'],
        del content['student_id'],
        del content['specialization'],
        del content['hours'],
        del content['grade'],
        del content['total_gpa'], 
        del content['state']

        return content , student
   
    def add_remaining_hours(self,content):
        


        i = 0
        for section in content:
            for sub_section in content[section]:
                completed_hours = sum(
                    int(course['hours']) for course in content[section][sub_section]
                    if course['total'] is not None and int(course['total']) > 50
                )

                content[section][sub_section] = {
                    'courses': content[section][sub_section],
                    'remaining_hours': self.FULL_HOURS[i] - completed_hours
                }

                i += 1
            return content    
        


