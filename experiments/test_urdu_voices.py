
import asyncio
import edge_tts

TEXT = (
    "Achha, samajh gaya. Aap ka internet slow chal raha hai, "
    "koi baat nahi. Chaliye, pehle router restart karke dekhte hain."
)

async def main():
    voices = [
        ("ur-PK-AsadNeural", "urdu_male.mp3"),
        ("ur-PK-UzmaNeural", "urdu_female.mp3"),
    ]

    for voice, filename in voices:
        try:
            communicate = edge_tts.Communicate(
                text=TEXT,
                voice=voice,
                rate="-10%",
                pitch="-2Hz",
            )
            await communicate.save(filename)
            print(f"Saved {filename} using {voice}")
        except Exception as exc:
            print(f"Failed {voice}: {exc}")

asyncio.run(main())
