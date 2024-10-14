import asyncio
from controllers import TranscriptController, LLMController
from models import CollegeCredentials
from pathlib import Path

# Create CollegeCredentials and TranscriptController
cardentails = CollegeCredentials(username='20210605', password='30403252103092')
downloader = TranscriptController(cardentails)


controller = LLMController()

result = controller.process("where to eat pasta")
print(result)

