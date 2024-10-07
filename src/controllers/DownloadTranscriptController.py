import requests
import os
import shutil
from models import CollegeCredentials
from helpers.config import Settings, get_settings

settings = get_settings()

class DownloadTranscriptController:
    def __init__(self, credentials: CollegeCredentials) -> None:
        self.username = credentials.username
        self.password = credentials.password
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/json"
        }
        self.pdf_directory = "pdf"
        self.ensure_pdf_directory()

    def ensure_pdf_directory(self):
        if not os.path.exists(self.pdf_directory):
            os.makedirs(self.pdf_directory)

    def login(self) -> bool:
        login_url = settings.COLLEGE_SCRAPING_SITE
        login_data = {"username": self.username, "password": self.password}
        login_response = self.session.post(login_url, json=login_data, headers=self.headers)

        if login_response.status_code == 200:
            print("Login successful!")
            return True
        else:
            print(f"Login failed. Status code: {login_response.status_code}")
            return False

    def download_transcript(self) -> str:
        download_url = settings.TRANSCRIPT_DOWNLOAD_LINK.format(username=self.username)
        print(f"Attempting to download transcript from: {download_url}")

        download_response = self.session.get(download_url, allow_redirects=True)
        if download_response.status_code == 200:
            filename = f"transcript-{self.username}.pdf"
            temp_path = filename
            with open(temp_path, 'wb') as f:
                f.write(download_response.content)
            print(f"Transcript downloaded successfully as {filename}")
            return temp_path
        else:
            print(f"Failed to download transcript. Status code: {download_response.status_code}")
            return ""

    def process(self) -> str:
        if self.login():
            temp_path = self.download_transcript()
            if temp_path:
                final_path = os.path.join(self.pdf_directory, os.path.basename(temp_path))
                shutil.move(temp_path, final_path)
                print(f"Transcript moved to {final_path}")
                return final_path
            else:
                print("Download failed. No transcript to move.")
                return ""
        else:
            print("Login failed. Cannot proceed with downloading the transcript.")
            return ""