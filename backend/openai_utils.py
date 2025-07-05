import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# def transcribe_audio(file_path):
#     with open(file_path, "rb") as audio_file:
#         transcript = openai.Audio.transcribe(
#             file=audio_file,
#             model="whisper-1",
#             response_format="text"
#         )
#     return transcript

# def translate_text(text, target_language):
#     prompt = f"Translate the following English text to {target_language}:\n\n{text}"
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "system", "content": "You are a professional translator."},
#             {"role": "user", "content": prompt}
#         ]
#     )
#     return response.choices[0].message.content


import openai

def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript.text

def translate_text(text, target_language):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Translate this to {target_language}"},
            {"role": "user", "content": text}
        ],
        temperature=0,
        max_tokens=1000
    )
    return response.choices[0].message.content