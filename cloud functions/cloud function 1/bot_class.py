from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update
import replica
import boto3
import json
import os

# Подготовка и получение переменных
BOT_TOKEN = os.getenv('BOT_TOKEN')
boto_session = boto3.session.Session(
                                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'), 
                                    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')) 

ymq_queue = boto_session.resource(
    service_name='sqs',
    endpoint_url='https://message-queue.api.cloud.yandex.net',
    region_name='ru-central1'
).Queue(os.environ.get('YMQ_QUEUE_URL'))


# События 
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text=replica.START_DEF)

async def default_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text=replica.DEFAULT_DEF)

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        voice = update.message.voice
        file_id = voice.file_id
        duration = voice.duration
        voice_file = await context.bot.get_file(file_id)
        
        ymq_queue.send_message(MessageBody=json.dumps({'file_path':voice_file.file_path, 'chat_id':update.message.chat_id}))
        await update.message.reply_text(text='Ваше сообщение обрабатывается')
        await update.message.reply_text(text=f'{voice_file.file_path} {update.message.chat_id} {duration}')

    except:
        await update.message.reply_text(text=replica.ERROR_TRANSLATE)

# Инициализация бота
class Bot:
    def __init__(self):
        self.application = ApplicationBuilder().token(BOT_TOKEN).build()
        self.add_user_handlers()
    
    def add_user_handlers(self):
        start = CommandHandler(['start', 'menu'], start_handler)
        default = MessageHandler(filters.ALL, default_handler)
        voice = MessageHandler(filters.VOICE, voice_handler)
        
        self.application.add_handler(start)
        self.application.add_handler(voice)
        self.application.add_handler(default)
    
    async def cloud_run(self, event):
        try:
            await self.application.initialize()
            for message in event["messages"]:
                await self.application.process_update(Update.de_json(json.loads(message["details"]["message"]["body"]), self.application.bot))
                return 'Success'
        except:
            return 'Failure'
