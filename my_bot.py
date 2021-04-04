import telebot
from rutimeparser import parse
import datetime
import requests
import pymorphy2
import nltk
morph = pymorphy2.MorphAnalyzer()

import config
bot = telebot.TeleBot(config.BOT_TOKEN)


@bot.message_handler(commands=['start', 'help'])  # Функция отвечает на команды 'start', 'help'
def start_message(message):
    bot.send_message(message.chat.id,
                     f"Привет! Я знаю погоду для Москвы и Санкт-Петербурга.\n"
                     f"Просто напиши мне в каком городе и на какой день хочешь узнать погоду.\n"
                     f"Для того, чтобы закончить диалог, напиши /bye.\n")
    
    
@bot.message_handler(commands=['bye'])  # Функция отвечает на команду 'bye'
def end_message(message):
    bot.send_message(message.chat.id,
                     f"Рад был помочь! До встречи!\n")
    
    
@bot.message_handler(content_types=['text'])  # Функция обрабатывает текстовые сообщения
def in_text(message):
    if message.text.lower() in ("привет", "прив", "hi", "yo", "йоу"):
        bot.send_message(message.from_user.id, "Привет! В каком городе и на какой день хочешь узнать погоду?")
    elif message.text.lower() in ("пока", "пок", "hi"):
        bot.send_message(message.from_user.id, "Рад был помочь! До встречи!")
    else:
        dt, loc, city = get_info(message.text)
        if dt == None:
            if not loc:
                bot.send_message(message.chat.id, 'Я тебя не понимаю. Напиши /help.')
            else:
                bot.send_message(message.chat.id, 'Ты не указал дату или я понял её неправильно. Спроси меня снова.')
        elif dt == 'no':
            bot.send_message(message.chat.id,
                            f'Я знаю погоду только на сегодня и пять дней вперед((. Спроси меня снова.\n'
                            f'Если ты указал день недели, то добавь к вопросу "следующий".')
        elif not loc:
            bot.send_message(message.chat.id, 'Я знаю погоду только для Москвы и Санкт-Петербурга. Спроси меня снова.')
        else:
            forecast = get_weather(loc, dt, city)
            bot.send_message(message.chat.id, text=forecast, parse_mode='HTML')
            bot.send_message(message.chat.id, text='Я могу еще чем-то помочь?\nЕсли нет, то попрощайся со мной или напиши /bye.')
        
              
def get_info(text):
    date = parse(text)
    if type(date) == datetime.datetime:
        date = date.date()

    tokenizer = nltk.tokenize.TreebankWordTokenizer()
    words = tokenizer.tokenize(text)
    res = []
    for word in words:
        p = morph.parse(word)[0]
        res.append(p.normal_form)
    loc = None
    city = None
    for word in res:
        if word in config.spb:
            loc = config.locations["spb"]
            city = 'Санкт-Петербурге'
        elif word in config.msk:
            loc = config.locations["msk"]
            city = 'Москве'

    if date:
        if date > (datetime.datetime.now() + datetime.timedelta(days=5)).date() or date < datetime.datetime.now().date():
            date = 'no'
        
    return date, loc, city

def get_weather(loc, dt, city):
    url = config.WEATHER_URL.format(lon=loc["lon"],
                             lat=loc["lat"],
                             token=config.WEATHER_TOKEN)
    res = requests.get(url)
    data = res.json()
    ex = '<b>{date}</b> в {city} будет <b>{desc}</b>.\nТемпература днем составит <b>{tem}</b>°.\nМинимальная температура: {mn}°\nМаксимальная температура: {mx}°\n\n'
    msg = ''
    for i in data['daily']:
        if datetime.date.fromtimestamp(i['dt']) == dt:
            msg += ex.format(date=datetime.datetime.fromtimestamp(i['dt']).strftime('%Y-%m-%d'),
                             city=city,
                             desc=i['weather'][0]['description'],
                             tem='{0:+1.0f}'.format(i['temp']['day']),
                             mn='{0:+1.0f}'.format(i['temp']['min']),
                             mx='{0:+1.0f}'.format(i['temp']['max'])
                    )

    return msg

bot.polling(none_stop=True, interval=0)