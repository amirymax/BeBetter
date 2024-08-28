from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from player import Player
from vars import Token, categories
from levels import *

bot = Bot(token=Token)
dp = Dispatcher(bot)

# Храним данные пользователей (на реальном сервере лучше использовать БД)
players = {}

hello_text = 'Приветсвуем! \n\nЭтот бот поможет тебе повысить свой уровень как физически, так и умственно!\n\nНу что, начнем?'


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    # Создаем нового игрока и сохраняем его в словарь по user_id
    players[message.from_user.id] = Player(user_id=message.from_user.id)

    # Кнопка для начала
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("Да, начнем!")]], resize_keyboard=True)
    await bot.send_message(message.from_user.id,
                           hello_text,
                           reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Да, начнем!")
async def ask_name(message: types.Message):
    await bot.send_message(message.from_user.id, "Как тебя зовут?")
    # Устанавливаем состояние "ожидания имени"
    players[message.from_user.id].state = "awaiting_name"


@dp.message_handler(lambda message: players[message.from_user.id].state == 'awaiting_name')
async def choose_category(message: types.Message):
    player = players[message.from_user.id]
    player.set_name(message.text)
    await bot.send_message(message.from_user.id, f"Приятно познакомиться, {player.name}! Чем ты занимаешься?")
    player.state = "awaiting_category"

    category_text = "Выбери категорию, которая наиболее близка к твоей деятельности:"
    science = KeyboardButton('Наука')
    art = KeyboardButton('Искусство')
    health = KeyboardButton('Медицина')
    sport = KeyboardButton('Спорт')
    it = KeyboardButton('IT')
    business = KeyboardButton('Бизнес')
    keyboard = ReplyKeyboardMarkup(
        one_time_keyboard=True, resize_keyboard=True)
    keyboard.add(it, science, business)
    keyboard.add(sport, health, art)
    # Отправляем пользователю описания категорий
    await bot.send_message(message.from_user.id, category_text, reply_markup=keyboard)
    all_categories = ''
    number = 1
    for category, data in categories.items():
        description = data['description']
        all_categories += f"{number}. {category}:\n{description}\n\n"
        number += 1
    await bot.send_message(message.from_user.id, all_categories)

    player.state = 'awaiting_category'


@dp.message_handler(lambda message: players[message.from_user.id].state == 'awaiting_category')
async def perform_task(message: types.Message):
    player: Player = players[message.from_user.id]
    chosen_category = message.text
    player.set_category(chosen_category)
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton('Готов!')]], resize_keyboard=True, one_time_keyboard=True)

    await bot.send_message(message.from_user.id, f'Итак, {player.name}, имя и вид деятельности теперь известны. Пора начать игру! \n\nТы готов ? ', reply_markup=keyboard)
    player.state = 'awaiting_game'


@dp.message_handler(lambda message: players[message.from_user.id].state == 'awaiting_game')
async def game_begins(message: types.Message):
    player: Player = players[message.from_user.id]
    title = level1['articles'][player.category]['title']
    link = level1['articles'][player.category]['link']
    keyboard = ReplyKeyboardMarkup([[KeyboardButton('Прочел. К вопросам')]], resize_keyboard=True, one_time_keyboard=True)
    message_text = f'Первый уровень состоит из двух этапов \n\n1-й этап: \nПрочитать статью по выбранной категории {player.category}:\n\n[{title}]({link})'
    await bot.send_message(message.from_user.id, message_text, parse_mode="markdown")
    await bot.send_message(message.from_user.id, 'После прочтения, нажмите кнопку внизу, чтобы ответит на вопросы про статью.' +
                           '\nЕсли ваши правильные ответы состовят выше 80%, вы проходите на следующий этап.', reply_markup=keyboard)
    player.state = 'reading_article'




if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
