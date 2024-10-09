from controllers import TranscriptController
from models import CollegeCredentials

cardentails = CollegeCredentials(username = '20210605' , password='30403252103092')
downloader = TranscriptController(cardentails)

print(downloader.process())