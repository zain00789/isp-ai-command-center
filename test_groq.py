
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv(override=True)

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
    api_key=os.environ["GROQ_API_KEY"]
)

response = llm.invoke(
    "Assalam-o-Alaikum! Roman Urdu mein jawab dein."
)

print("Groq response:", response.content)
