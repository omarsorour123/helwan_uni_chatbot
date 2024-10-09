from controllers import TranscriptController
from models import CollegeCredentials

cardentails = CollegeCredentials(username = '' , password='')
downloader = TranscriptController(cardentails)

print(downloader.process())