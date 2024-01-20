from telegram import Update
from bot_class import Bot
import asyncio
import json

def handler(event: dict, context: str):
    result = asyncio.get_event_loop().run_until_complete(Bot().cloud_run(event))
    return {
        'statusCode': 200,
        'body': result
    }
