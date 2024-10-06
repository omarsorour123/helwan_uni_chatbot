from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    GEMINI_API_KEY:str
    COLLEGE_SCRAPING_SITE:str
    TRANSCRIPT_DOWNLOAD_LINK:str

    class config:

        env_file = '.env'
        env_file_encoding = "utf-8"