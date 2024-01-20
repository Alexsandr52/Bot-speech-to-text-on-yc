import assemblyai as aai
import requests
import asyncio
import json
import os

token = os.getenv('BOT_TOKEN') 
aai.settings.api_key = os.getenv('API_KEY')
config = aai.TranscriptionConfig(language_code='ru')
transcriber = aai.Transcriber(config=config)

def transcribe_voice(file_path: str):
    try:
        transcript = transcriber.transcribe(file_path)
        text = transcript.text
    except:
        text = 'Что то пошло не так'
    return text

def send_message(text, chat_id):
    url_req = 'https://api.telegram.org/bot' + token + '/sendMessage' + '?chat_id=' + str(chat_id) + '&text=' + text
    results = requests.get(url_req)
    return results


def handler(event, context):
    
    for message in event['messages']:
        geted_json = json.loads(message['details']['message']['body'])
        file_path = geted_json['file_path']
        chat_id = geted_json['chat_id']
        
        result = transcribe_voice(file_path)
        results = send_message(result, chat_id)
        
        
    return {
        'statusCode': 200,
        'body': results,
    }