
import asyncio
import edge_tts

async def main():
    text = (
        "السلام علیکم! آپ کا انٹرنیٹ سست چل رہا ہے۔ "
        "پریشان نہ ہوں، میں آپ کی مدد کرتا ہوں۔"
    )

    communicate = edge_tts.Communicate(
        text=text,
        voice="ur-PK-AsadNeural"
    )

    await communicate.save("urdu_voice_test.mp3")
    print("Urdu voice saved to urdu_voice_test.mp3")

asyncio.run(main())
