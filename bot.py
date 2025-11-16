import telebot
from config import *
from logic import *

bot = telebot.TeleBot(TOKEN)

user_colors = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, """
Доступные команды: 
 /show_city [город] - показать город на карте
 /remember_city [город] - запомнить город
 /show_my_cities - показать все запомненные города
 /set_color [цвет] - установить цвет маркеров (red, blue, green, purple, orange, black)
 /current_color - показать текущий цвет маркеров
 /show_cities_in_country [страна] - показывает 25 городов определённой страны
                     """)


@bot.message_handler(commands=['set_color'])
def handle_set_color(message):
    user_id = message.chat.id
    parts = message.text.split()
    color = parts[1].lower()
    valid_colors = ['red', 'blue', 'green', 'purple', 'orange', 'black']
    
    if color in valid_colors:
        user_colors[user_id] = color
        bot.send_message(message.chat.id, f'Цвет маркеров установлен: {color}')
    else:
        bot.send_message(message.chat.id, f'Неверный цвет! Доступные цвета: {", ".join(valid_colors)}')

@bot.message_handler(commands=['current_color'])
def handle_current_color(message):
    user_id = message.chat.id
    color = user_colors.get(user_id)
    bot.send_message(message.chat.id, f'Текущий цвет маркеров: {color}')



@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    user_id = message.chat.id
    city_name = message.text.split()[-1]
    color = user_colors.get(user_id, 'blue')
    manager.create_grapf(f'{user_id}.png', [city_name], color=color)
    with open(f'{user_id}.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo)


@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    user_id = message.chat.id
    city_name = message.text.split()[-1]
    if manager.add_city(user_id, city_name):
        bot.send_message(message.chat.id, f'Город {city_name} успешно сохранен!')
    else:
        bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    cities = manager.select_cities(message.chat.id)
    if cities:
        color = user_colors.get(message.chat.id, 'blue')
        manager.create_grapf(f'{message.chat.id}_cities.png', cities, color=color)
        with open(f'{message.chat.id}_cities.png', 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
    else:
        bot.send_message(message.chat.id, 'У вас пока нет сохранённых городов.')

@bot.message_handler(commands=['show_cities_in_country'])
def handle_show_cities_in_country(message):
    user_id = message.chat.id
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.send_message(user_id, "Укажите страну: /show_cities_in_country [страна]")
    country_name = parts[1].strip()
    cities = manager.get_cities_in_country(country_name)
    if not cities:
        return bot.send_message(user_id, f"Города в '{country_name}' не найдены.")
    color = user_colors.get(user_id, 'blue')
    filename = f'{user_id}_country_{country_name.replace(" ", "_")}.png'
    manager.create_grapf(filename, cities, color=color)
    with open(filename, 'rb') as f:
        bot.send_photo(user_id, f, caption=f"{country_name}: {len(cities)} городов")

if __name__=="__main__":
    manager = DB_Map(DATABASE)
    bot.polling()
