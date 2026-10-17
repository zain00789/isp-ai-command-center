import asyncio
import edge_tts

async def main():
    communicate = edge_tts.Communicate(
        "Hello! Welcome to ISP AI Command Center.",
        "en-US-AriaNeural"
    )
    await communicate.save("test_voice_reply.mp3")
    print("Saved test_voice_reply.mp3")

asyncio.run(main())