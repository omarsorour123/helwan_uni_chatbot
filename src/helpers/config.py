from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    GEMINI_API_KEY:str
    COLLEGE_SCRAPING_SITE:str
    TRANSCRIPT_DOWNLOAD_LINK:str
    EXTRACT_STUDENT_INFORMATION_PROMPT:str
    class config:

        env_file = '.env'
        env_file_encoding = "utf-8"


def get_settings():
    return Settings()
