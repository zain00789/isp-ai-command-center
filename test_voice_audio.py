
import base64
import json
import urllib.request

url = "http://127.0.0.1:8000/api/v1/voice/ask-and-speak"

with open("test_audio.ogg", "rb") as audio_file:
    audio_data = audio_file.read()

boundary = "----VoiceTestBoundary"
body = (
    f"--{boundary}\r\n"
    'Content-Disposition: form-data; name="file"; filename="test_audio.ogg"\r\n'
    "Content-Type: audio/ogg\r\n\r\n"
).encode() + audio_data + f"\r\n--{boundary}--\r\n".encode()

request = urllib.request.Request(
    url,
    data=body,
    headers={
        "Content-Type": f"multipart/form-data; boundary={boundary}"
    },
    method="POST",
)

with urllib.request.urlopen(request) as response:
    result = json.loads(response.read())

with open("ai_reply.mp3", "wb") as output:
    output.write(base64.b64decode(result["audio_base64"]))

print("Transcription:", result["transcription"])
print("AI action:", result["ai"]["action"])
print("MP3 saved as ai_reply.mp3")
