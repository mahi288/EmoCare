import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


def generate_chat_title(conversation):

    prompt = f"""
You are generating a title for a mental health chat.

Rules:
- Maximum 5 words.
- No quotation marks.
- Professional.
- Meaningful.
- Don't write 'Conversation' or 'Chat'.
- Only output the title.

Conversation:
{conversation}
"""

    response = model.generate_content(prompt)

    return response.text.strip()