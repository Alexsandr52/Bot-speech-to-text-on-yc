# Bot Speech To Text On Yandex Cloud

[![Yandex Cloud](https://storage.yandexcloud.net/cloud-www-assets/region-assets/ru/light/desktop/logo.svg)](https://console.cloud.yandex.ru)

Этот проект представляет собой туториал, по написанию бота для [telegram](https://web.telegram.org/), используя Python и сервисы [Yandex Cloud](https://console.cloud.yandex.ru). Идея для бота звучала так: 
__"Бот который будет транскрибировать текст из аудио (в лучшем случае его можно добавить в чат с друзьями)".__

### 1. Создание бота 🤖
Начало, как и у всех ботов примитивное, используя [@BotFather](https://telegram.me/BotFather), c помощью /newbot создаем бота. Используйте любые настройки какие хотите. Нам важно лишь получить его `HTTP API TOKEN`.

### 2. Начало работы с облаком ☁️
Что бы понять, что из себя представляет [Yandex Cloud](https://cloud.yandex.ru/ru/) советую посетить эту ссылку. Мы же двинемся дальше. Если вы первый раз пользуйтесь облаком вам придется создать [платежный аккаунт](https://cloud.yandex.ru/ru/docs/billing/concepts/billing-account). Не волнуйтесь яндекс берет копейки и дает гранты на создание сервисов. [Как создать платежный аккаунт 📙 ](https://cloud.yandex.ru/ru/docs/billing/quickstart/).

### 3. Сервисы Yandex Cloud которые будем использовать ☁️🧱
Мы будем использовать: 
> [`Cloud Functions`](https://cloud.yandex.ru/ru/docs/functions/). 
> [`API Gateway`](https://cloud.yandex.ru/ru/docs/api-gateway/).
> [`Message Queue`](https://cloud.yandex.ru/ru/docs/message-queue/). 
>  Другие сервисы не вошедшие в этот список будут использованы однократно.

### 4. Начнем создавать нашего бота 🧰⚒️
Есть полное [руководство 📙](https://cloud.yandex.ru/ru/docs/api-gateway/tutorials/telegram-bot-serverless) как создать бота самому. Но в нем не пункта про [`Message Queue`](https://cloud.yandex.ru/ru/docs/message-queue/) и язык для функции Node.js. Вы можете воспользоваться этим руководством и далее вернуться сюда (пункт "5. Функционал бота"). В общем выбор за вами. Я же предлагаю более автоматизированное решение. 

> Главное меню называют консоль.

 В консоли, на верхней панели выбираем "Сервисные аккаунты", жмем "Создать сервисный аккаунт". Из интересного здесь роли, поля типа "имя" заполняйте сами. Ради безопасности вы можете найти [описание ролей](https://cloud.yandex.ru/ru/docs/iam/concepts/access-control/roles) и дать ему только те, что необходимы. Я же дам ему временно роль **admin**.

![Alt text](3.png)
 
 В консоли, выбираем сервис `Lockbox`, создаем секрет. Имя выберите сами, друге настройки не трогайте. Ключ, это "TG_TOKEN", значение токен вашего бота. Так же скопируйте "Идентификатор версии" вашего `Lockbox`.

![Alt text](1_2.png)

В консоли выбираем сервис `Cloud Apps`, жмем "Установить приложение", выбираем "Demo Telegram Bot". Наполняем поля "Имя", "Сервисный аккаунт" (который мы создали ранее), "Идентификатор секрета Yandex Lockbox" и "Идентификатор версии секрета Yandex Lockbox". "Сервисный аккаунт" советую не ставить автоматически, так как на (20.01.24), это криво работает. Жмем "Установить". Установка занимает время. Если вы получили ошибку пойдите все шаги заново. В случае успеха советую удалить `Lockbox`, так как по тарифам Yandex Cloud он много потребляет. 

![Alt text](4.png)

# ❗❗❗ Про `Lockbox`  
`Lockbox` - сервис для хранения секретов. Той информации которую нельзя раскрывать, но нужно использовать. Если вы планируете делать бота боевым, то советую все токены и подобные переменные переносить туда. Далее мы будем использовать вместо `Lockbox` переменные окружения, но алгоритм подключения тот же.

Теперь нам нужен `WebHook`. Это самая непонятная для многих часть, по этому попытаюсь объяснить. В главном меню выбираем `API Gateway` заходим в обзор. Видим что-то такое.
```
openapi: "3.0.0"
info:
  version: 1.0.0
  title: Test API
servers:
- url: https://d5d12lonn1r16h60eu9d.apigw.yandexcloud.net
paths:
  /echo:
    post:
      x-yc-apigateway-integration:
        type: cloud_ymq
        action: SendMessage
        queue_url: https://message-queue.api.cloud.yandex.net/b1govmlmj2lp1vuhvlms/dj600000001a902a03ap/tg-bot-app-dt9fjobbc07r0qbdbsgj
        folder_id: b1g26vk6l5qulgv71cfi
        delay_seconds: 0
        service_account_id: ajeqs2cau6u0g13q6us2
```
Прочитать это можно так. Мы ждем что telegram отправит нам что-то "**json**" на "https://d5d12lonn1r16h60eu9d.apigw.yandexcloud.net"<Служебный домен> и мы получив "**json**", выполним **post**. А именно отправим этот "**json**" в очередь сообщений [`Message Queue`](https://cloud.yandex.ru/ru/docs/message-queue/). Адес у нее "https://message-queue.api.cloud.yandex.net/b1govmlmj2lp1vuhvlms/dj600000001a902a03ap/tg-bot-app-dt9fjobbc07r0qbdbsgj". Так что наш `WebHook` мы должны установить на "https://d5d12lonn1r16h60eu9d.apigw.yandexcloud.net". 

Для этого в Windows открываем powershell. И выполняем эту команду.
```
curl.exe `
 --request POST `
 --url https://api.telegram.org/bot<токен бота>/setWebhook?url=<Служебный домен>/echo
```

Для Linux и Mac terminal. (Не селен в их терминале может не так должна выглядеть команда).
```
curl -X POST "https://api.telegram.org/bot<токен бота>/setWebhook?url=<Служебный домен>/echo"
```

- <Токен бота> - тот что с [@BotFather] (https://telegram.me/BotFather).
- <Служебный домен> - в `API Gateway` в обзоре.

Хороший результат.
![Alt text](6.png)
```
{"ok":true,"result":true,"description":"Webhook was set"}
```

Теперь мы почти можем пользоваться ботом. Для того что бы он сказал первые слова, заходим в [`Cloud Functions`](https://cloud.yandex.ru/ru/docs/functions/). Выбираем нашу функцию. Не пугайтесь что она на Node.js. Мы ее позже перепишем. и внизу под кодом ищем поле "**Секреты Yandex Lockbox**" (Если вы не удаляли Lockbox пропустите пункт и пишите боту). Удаляем это поле и в поле "**Переменные окружения**" добавляем ключ "**BOT_TOKEN**", значение "ваш токен". В самом низу кнопка сохранить изменения. Теперь можно писать боту.
![Alt text](8.png)

### Функционал бота (пишем код)👩‍💻
Для начала обсудим как работает бот. Если кто-то пропустил прошлый пункт. Наш бот сейчас получает телеграмма "**json**" и отправляет его в очередь сообщений (особо она не нужна. Принцип работы такой пока сообщение, но обработается, оно не выйдет из очереди и будет постоянно пытаться обработаться через функцию (которая может быть с ошибкой)), из очереди его достает триггер и отправляет в нашу функцию, которая уже что-то с ним делает. И так давайте перепишем ее.

# ❗❗❗  
 Важно отметить что я редактирую существующую функцию если хотите создать новую. Создайте новый триггер из очереди и пусть он отправляет сообщения в вашу новую функцию, старый триггер и функцию нужно удалить. Почитать можно [тут📙](https://cloud.yandex.ru/ru/docs/message-queue/tutorials/video-converting-queue#create-trigger) Ps. Пункт 5
 
Заходим в пункт "Редактор" и меняем параметр "Среда выполнения". В моем случае это "Python 3.12". Удаляем все файлы которы были и создаем свои. "index.py", "requirements.txt". [Зачем requirements.txt](https://cloud.yandex.ru/ru/docs/functions/lang/python/dependencies).

У функции в параметрах есть пункт "Точка входа" по умолчанию он "index.handler". Что значит из файла "index" будет вызвана функция "handler". Еще важно знать что в нее будут переданы 2 аргумента "event" и "context". Так и напишем.
```python
import json

def handler(event: dict, condext: str):
    for message in event['messages']:
        geted_json = json.loads(message['details']['message']['body'])
        print(geted_json)

    return {
        'statusCode': 200,
        'body': 'text',
    }
```
Цикл нужен, так как может прейти больше чем одно сообщение (не в нашей задаче, но все же). Если интересно, что в "**json**", сделайте "**print**" выше на сам "**event**". Но в нем точно будет `['details']['message']['body']`. После сохранения, пишу боту и вижу в логах функции.
```javaScript 
{
'update_id': 999999999, 
'message': {
    'message_id': 17, 
    'from': {
        'id': 999999999, 
        'is_bot': False, 
        'first_name': 'Мое Имя', 
        'last_name': 'Моя Фамилия', 
        'username': 'Мой тг', 
        'language_code': 'en'}, 
    'chat': {
        'id': 999999999, 
        'first_name': 'Мое Имя', 
        'last_name': 'Моя Фамилия', 
        'username': 'Мой тг', 
        'type': 'private'}, 
    'date': 1705748798, 
    'text': 'Привет, ты как ?'
    }
}
```
Сейчас мы умеем принимать сообщения и получать информацию.

И так. ```ctrl+c``` ```ctrl+v``` Этот код. 
```python
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
```
В будущем мы создадим файл "bot_class.py". Все остальное мы установим чрез [requirements.txt](https://cloud.yandex.ru/ru/docs/functions/lang/python/dependencies). 
Что делает этот код. Использует библиотеку asyncio для выполнения асинхронной функции Bot().cloud_run(event) в синхронном стиле. Давайте разберем, что происходит пошагово:
> `asyncio.get_event_loop()`: Получает текущий цикл событий asyncio для управления асинхронными операциями.
> `Bot().cloud_run(event)`: Вызывает метод `cloud_run` у объекта класса `Bot` с передачей аргумента `event`. Этот метод реализован как асинхронная функция (используя ключевое слово `async`), поскольку он вызывается в контексте asyncio.
> `.run_until_complete(...)`: Запускает выполнение асинхронной функции, переданной в качестве аргумента, до её завершения. Эта функция блокирует выполнение кода до завершения асинхронной операции.

Таким образом, код выполняет асинхронную функцию `Bot().cloud_run(event)` с использованием синхронной обертки `run_until_complete`, чтобы выполнить эту функцию в синхронном контексте. Обычно такой код используется в сценариях, где требуется синхронный стиль выполнения, но при этом используются асинхронные операции, например, в среде, поддерживающей асинхронное программирование.

requirements.txt
```
python-telegram-bot
boto3 # только тем кто читает до конца
```
У меня так же есть replica.py . Тут просто прячу ответы бота. 
```
START_DEF='Привет я могу распозновать текст голосовых сообщений 😁'
DEFAULT_DEF='Я пока могу отвечать только на голосовые 😢'
ERROR_TRANSLATE='Неполучилось распознать 😢'
```

Теперь bot_class.py Полный код выше в файле. Мы же разбер важные пункты.

**События**
```python
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update
import replica
import boto3
import json
import os

BOT_TOKEN = os.getenv('BOT_TOKEN')

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
        
        # ymq_queue.send_message(MessageBody=json.dumps({'file_path':voice_file.file_path, 'chat_id':update.message.chat_id}))
        await update.message.reply_text(text='Ваше сообщение обрабатывается')
        await update.message.reply_text(text=f'{voice_file.file_path} {update.message.chat_id}')

    except:
        await update.message.reply_text(text=replica.ERROR_TRANSLATE)
```
Такие функции служат для обработки каких либо действий. Которы мы укажем позже. Например, при получение команды /start мы в дальнейшем будем вызывать `start_handler()` которая отправит нам сообщение `replica.START_DEF`. Если вы пишите свои личные функции советую пользоваться [документацией](https://www.bing.com/search?q=python-telegram-bot&cvid=19751b2f68c74220884bbd0af63fff29&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQIxgnMgYIAhBFGDsyBggDEAAYQDIGCAQQABhAMgYIBRAAGEAyBggGEEUYPDIGCAcQRRg8MgYICBBFGDzSAQgxNjc0ajBqOagCALACAA&FORM=ANAB01&PC=NMTS) ибо гайды устаривают.

**Класс бота**
```python
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
```

При создании объекта класса будет вызван `__init__()` где будет создан `application` (грубо говоря наш бот), и к нему будут добавлены обработчики через функцию `add_user_handlers`. В этой функции мы создаем один из выбранных нами объектов обработки ([`CommandHandler`](https://docs.python-telegram-bot.org/en/v20.7/telegram.ext.commandhandler.html#commandhandler), [`MessageHandler`](https://docs.python-telegram-bot.org/en/v20.7/telegram.ext.messagehandler.html)). В `MessageHandle`r мы пользуемся [`filters`](https://docs.python-telegram-bot.org/en/v20.7/telegram.ext.filters.html) для указания на что реагировать. Дальше думаю все понятно.
Перейдем к функции `cloud_run()`. Похожий код да, как в `handler`, который мы писали что бы посмотреть на **json**. Ну и суть та же мы так же хотим получить этот **json**. И передать его нашему боту. Конечно мы ждем ответ. И далее или успех или провал.

Материалы которые я использовал.
> [Документация Yandex Cloud](https://cloud.yandex.ru/ru/docs) 
> [Документация python-telegram-bot](https://docs.python-telegram-bot.org/en/v20.7/)
> [Подробный туториал (отдельное спасибо)](https://www.youtube.com/watch?v=Mq5JocY6b1M&t=968s)

Теперь вы можете сами писать свои обработчики и возможно добавлять другие сервисы. Далее я буду рассматривать код лично своей задачи. Ps. Все переменные окружения нужно, по-хорошему хранить в `LockBox`.

# Распознавание текста в голосовых 🗣️ >🤖>📃

### Message Queue (очередь сообщений) 👥
Есть 2 основных пути. Использовать готовую нейронную сеть или написать свою. Пока что свою я еще не написал. По этому воспользуемся [assemblyai.com](https://www.assemblyai.com). Так же есть проблема, которую нам нужно обойти. Это время ответа для telegram. Так как assemblyai отвечает не сразу. Мы буквально заставляем telegram ждать наш ответ. Для решения Этой проблемы используем [`Message Queue`](https://cloud.yandex.ru/ru/docs/message-queue/). Полученное голосовое сообщение будем отправлять в очередь, после чего сразу отвечать. Наш голосовое будет забирать другая функция и после обработки отправит его обратно telegram как новое сообщение.

Начнем отправлять голосовые в очередь. Для этого создадим очередь. Я меняю только "Срок хранения сообщений" на 1 час ибо мне больше не нужно. Это касается сообщений, которые не смогли обработаться или ситуации, когда мы не успеваем обработать сообщение за час. "Настройки очередей недоставленных сообщений" нужны больше в боевых задачах. Что бы ваш триггер не пытался постоянно пропихнуть сообщение если у него вылезает ошибка. Но мне этот пункт не нужен. 
Пора изменить функцию, а именно файл "bot_class.py".
```python
BOT_TOKEN = os.getenv('BOT_TOKEN')
boto_session = boto3.session.Session(
                                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'), 
                                    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')) 

ymq_queue = boto_session.resource(
    service_name='sqs',
    endpoint_url='https://message-queue.api.cloud.yandex.net',
    region_name='ru-central1'
).Queue(os.environ.get('YMQ_QUEUE_URL'))
```

В "Переменные окружения" дописываем `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`. Это ключ и его id от сервисного аккаунта. У него должны быть определенные роли, но как я и говорил у моего стоит роль "**admin**" по этому проблем не будет. Получить их можно из главного меню зайдя в "Сервисные аккаунты" выбрав свой что создавали. Далее сверху "Создать новый ключ", "Создать статический ключ".

Пример
> `AWS_ACCESS_KEY_ID : YCAJEaIO6a1HB_18n7P5w1BIW`
> `AWS_SECRET_ACCESS_KEY : YCNqS1JcZJdtK2sq4uu7arxVaT4bnT_cLaJ989jS`

Так же нужна `YMQ_QUEUE_URL` тоже в "Переменные окружения". Соответственно ссылка на нашу очередь. Получить ее можно в обзоре очереди. Про [boto](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html), можно почитать на официальной [документации](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html), в документации когда читал не сразу нашел, что такое 'sqs' так, что вот вам [ссылка](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/sqs.html#sqs). Скажу только что мы создаем объект, который может взаимодействовать с нашей очередью `ymq_queue`.

Теперь изменим функцию `voice_handler`.
```python
async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        voice = update.message.voice
        file_id = voice.file_id
        duration = voice.duration
        voice_file = await context.bot.get_file(file_id)
        
        # Добавленная строка
        ymq_queue.send_message(MessageBody=json.dumps({'file_path':voice_file.file_path, 'chat_id':update.message.chat_id}))

        await update.message.reply_text(text='Ваше сообщение обрабатывается')
        # await update.message.reply_text(text=f'{voice_file.file_path} {update.message.chat_id}')
        
    except:
        await update.message.reply_text(text=replica.ERROR_TRANSLATE)
```
Теперь мы получив голосовое отправляем его в нашу очередь в формате "**json**". Сообщение вида: 
```
{'file_path':voice_file.file_path, 'chat_id':update.message.chat_id}
```
chat_id нам важен, что бы знать кому слать ответ. Проверим на практике. После отправки голосового боту. Параметр "Сообщений в очереди" у очереди изменился на 1. Фуф тавтология. Пора вешать триггер. 

### Триггер и новая функция 👁️‍🗨️

Для начала создайте новую функцию. Язык так же Python.

Теперь создадим триггер. Тут все придельно просто. Заходим в `Cloud Functions` в левой панели выбираем триггеры и создаем новый. 
1. "Тип" меняем на `Message Queue`.
2. "Запускаемый ресурс" будет "Функция". 
3. "Очередь сообщений" выбираем ту, которую создавали и тд. 
4. "Сервисный аккаунт" с нужными правами.
5. "Функция" которую мы только, что создали.
6. "Тег версии функции" ставим `$lastest` 
7. "Сервисный аккаунт" с нужными правами.

Теперь код функции. Я создал с примером и тут все так же. Нам приходит "**json**". Мы его вскрываем и тащим что хотели. А именно наш `chat_id` и `file_path`. Идентификатор чата и ссылка на скачивание голосового соответственно. Так же надо реализовать алгоритм работы с "assemblyai".
requirements.txt
```
assemblyai==0.20.2
```
index.py
```python
import assemblyai as aai
import requests
import asyncio
import json
import os

token = os.getenv('BOT_TOKEN') 

# базовые настройки для assemblyai первая страница доки 
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

# Что бы отправить сообщение мы фармируем ссылку и делаем get 
def send_message(text, chat_id):
    url_req = 'https://api.telegram.org/bot' + token + '/sendMessage' + '?chat_id=' + str(chat_id) + '&text=' + text
    results = requests.get(url_req)
    return results
```


index.py handler 
Важно отметить, что вскрываем мы json так же как и раньше. 
```python

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
```

Вот и все. Можно добавить еще пару вещей, типа обработки длинны голосового и тд. Но это уже другая история. Надеюсь ком-то это было полезно. Спасибо за внимание ❤️
