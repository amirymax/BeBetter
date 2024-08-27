from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from player import Player
from vars import Token
from vars import categories
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


@dp.message_handler(lambda message: players[message.from_user.id].state == "awaiting_name")
async def set_name(message: types.Message):
    player = players[message.from_user.id]
    player.set_name(message.text)
    await bot.send_message(message.from_user.id, f"Приятно познакомиться, {player.name}! Чем ты занимаешься?")
    player.state = "awaiting_category"


@dp.message_handler(lambda message: players[message.from_user.id].state == 'awaiting_category')
async def choose_category(message: types.Message):
    category_text = "Выбери категорию, которая наиболее близка к твоей деятельности:"
    categories_buttons = [KeyboardButton(category)
                          for category in categories.keys()]
    science = KeyboardButton('Наука')
    art = KeyboardButton('Искусство')
    health = KeyboardButton('')
    keyboard = ReplyKeyboardMarkup(
        [categories_buttons], one_time_keyboard=True, resize_keyboard=True)

    # Отправляем пользователю описания категорий
    await bot.send_message(message.from_user.id, category_text, reply_markup=keyboard)
    all_categories = ''
    number = 1
    for category, data in categories.items():
        description = data['description']
        all_categories += f"{number}. {category}:\n{description}\n\n\n"
        number += 1
    await bot.send_message(message.from_user.id, all_categories)

    players[message.from_user.id].state = 'awaiting_task'


@dp.message_handler(lambda message: players[message.from_user.id].state == 'awaiting_task')
async def perform_task(message: types.Message):
    chosen_category = message.text
    tasks = categories.get(chosen_category)
    if not tasks:
        await bot.send_message(message.from_user.id, "Извините, произошла ошибка. Попробуйте снова.")
        return

    task_text = f"Первый уровень, задания для категории '{chosen_category}':\n\n1. {tasks['tasks'][0]}\n2. {tasks['tasks'][1]}"
    await bot.send_message(message.from_user.id, task_text)
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
