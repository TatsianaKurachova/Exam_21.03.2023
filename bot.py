import requests
import telebot
import random
import datetime
import sqlite3 
import csv
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv, dotenv_values

load_dotenv()
config = dotenv_values(".env")

bot = telebot.TeleBot(config['TOKEN'], parse_mode=None)

conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Чем я могу помочь:\n получить курс валют /course \n показать кота /cat \n показать курс биткоина /btc\n выдать шутку /joke \n выводит рецепт /food\n сыграем в игру? /game \n вывести время /time \n получить смайл /sticker \n получить данные о разработчике бота /sw \n регистрация пользователя /registration \n получить данные о фильме /movies")


@bot.message_handler(commands=['time'])
def get_current_time(message):
    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    bot.reply_to(message, f"Текущее время: {current_time}")


@bot.message_handler(commands=['course'])
def show_exchange_rates(message):
    response = requests.get(config['BANK_API']).json()
    for i in list(response):
        if i['Cur_Abbreviation'] == 'USD':
            usd_exchange_rate = i['Cur_OfficialRate']
        if i['Cur_Abbreviation'] == 'EUR':
            euro_exchange_rate = i['Cur_OfficialRate']
        if i['Cur_Abbreviation'] == 'PLN':
            pln_exchange_rate = i['Cur_OfficialRate']
    bot.send_message(message.chat.id, f'today cost of one BYN - {usd_exchange_rate} USD, {euro_exchange_rate} EUR, {pln_exchange_rate} PLN')


@bot.message_handler(commands=['cat'])
def get_dog(message):
    response = requests.get(config['CAT_URL'])
    data= response.json()
    image_url = data[0]['url']
    bot.send_photo(message.chat.id, image_url)


@bot.message_handler(commands=['btc'])
def get_btc_info(message):
    response = requests.get(config['BANK_URL']).json()
    btc_data = ''
    for data in response[:5]:  
        symbol = data['symbol']
        last_price = data['lastPrice']
        price_change_percent = data['priceChangePercent']
        btc_data += f'\n{symbol}: {last_price} ({price_change_percent}%)'
    bot.send_message(message.chat.id, btc_data)


@bot.message_handler(commands=['joke'])
def get_joke(message):
    response = requests.get(config['JOKE_URL'])
    data = response.json()
    if data['type'] == 'twopart':
        joke = data['setup'] + '\n' + data['delivery']
    elif data['type'] == 'single':
        joke = data['joke']
    bot.reply_to(message, joke)


@bot.message_handler(commands=['food'])
def send_food(message):
    response = requests.get(config['FOOD_URL'])
    data = response.json()['meals'][0]
    food_name = data['strMeal'] 
    picter_food = data['strMealThumb']
    category_food = data['strCategory']
    ingredients = [] 
    for i in range(1, 20):
        if data[f'strIngredient{i}'] != "":
            ingredient = data[f'strMeasure{i}'].strip() + " " + data[f'strIngredient{i}'].strip() 
            ingredients.append(ingredient)
    recipe = data['strInstructions'] 
    response_message = f"<b>{food_name}</b>\n{category_food}\n{picter_food}\nИнгредиенты:\n"
    for ingredient in ingredients:
        response_message += f"- {ingredient}\n"
    response_message += f"\nПриготовление:\n{recipe}"
    bot.send_message(message.chat.id, response_message, parse_mode='HTML')


@bot.message_handler(commands=['sticker'])
def send_sticker(message):
    response = requests.get(config['SMILE_URL'])
    sticker_url = response.json()['link']
    bot.send_sticker(message.chat.id, sticker_url)


@bot.message_handler(commands=['sw'])
def handle_sw_command(message):
    msg = "Разработчик этого бота - Курачева Татьяна\nОбразование: магистратура\n\nКонтакты: timoha-tatiana@mail.ru"
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['registration'])
def handle_registration_command(message):
    cursor.execute(f"SELECT COUNT(*) FROM users WHERE id={message.chat.id}")
    result = cursor.fetchone()
    if result[0] > 0:
        bot.send_message(message.chat.id, "Вы уже зарегистрированы.")
    else:
        cursor.execute(f"INSERT INTO users (id) VALUES ({message.chat.id})")
        conn.commit()
        bot.send_message(message.chat.id, "Вы успешно зарегистрировались.")


with open('movies.csv', encoding='utf-8') as file:
    reader = csv.reader(file)
    movies = list(reader)

@bot.message_handler(commands=['movies'])
def send_movie(message):
    movie = random.choice(movies)
    text = f'Порядковый номер: {movie[0]}\nНазвание и год выпуска: {movie[1]}\nСсылка: {movie[2]}\n Описание: {movie[3]}\n'
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['game'])
def start_message(message):
    global num, chance
    num = random.randint(1, 100)
    chance = 3
    bot.reply_to(message, 'Привет!\nДавай сыграем в "угадай число."\nЯ загадал число от 1 до 100!\nУ тебя есть 3 попытки.')


@bot.message_handler(func=lambda message: True)
def game(message):
    global chance, num
    answer = int(message.text.strip())
    if answer == num:
        bot.reply_to(message, f'Ура! Ты угадал {num}!')
        start_message(message)

    elif answer < num:
        chance -= 1
        if chance > 0:
            bot.reply_to(message, f'{answer} меньше, чем мое число! Попробуй ещё раз. У тебя осталось {chance} попыток.')
        else:
            bot.reply_to(message, f'К сожалению, ты не угадал{num}. Попробуй ещё раз.')
            start_message(message)

    elif answer > num:
        chance -= 1
        if chance > 0:
            bot.reply_to(message, f'{answer} больше, чем мое число! Попробуй ещё раз. У тебя осталось {chance} попыток.')
        else:
            bot.reply_to(message, f'К сожалению, ты не угадал число {num}. Попробуй ещё раз')
            start_message(message)


bot.polling()
cursor.close()
conn.close()
