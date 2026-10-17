import os
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

audio = client.text_to_speech.convert(
    voice_id="cjVigY5qzO86Huf0OWal",  # Eric
    model_id="eleven_multilingual_v2",
    text="Assalam o Alaikum! Aap ka internet slow chal raha hai? Chaliye, main aap ki madad karta hoon.",
)

with Path("elevenlabs_test.mp3").open("wb") as file:
    for chunk in audio:
        file.write(chunk)

print("Saved elevenlabs_test.mp3")