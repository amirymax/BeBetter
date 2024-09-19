import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from player import Player
from vars import Token, categories
import random

# Загружаем данные из JSON файла
with open('levels.json', 'r', encoding='utf-8') as file:
    levels = json.load(file)


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
        [[KeyboardButton("Да, начнем!")]], resize_keyboard=True, one_time_keyboard=True)
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
    player: Player = players[message.from_user.id]
    player.set_name(message.text)

    category_text = f"_Приятно познакомиться,_ *{player.name}*!\n\nВыбери категорию, которая наиболее близка к твоей деятельности:"
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
    await bot.send_message(message.from_user.id, category_text, reply_markup=keyboard, parse_mode='markdown')
    all_categories = ''
    number = 1
    for category, data in categories.items():
        description = data['description']
        all_categories += f"*{number}. {category}:*\n{description}\n\n"
        number += 1
    await bot.send_message(message.from_user.id, all_categories, parse_mode='markdown')

    player.state = 'awaiting_category'


@dp.message_handler(lambda message: players[message.from_user.id].state == 'awaiting_category')
async def perform_task(message: types.Message):
    player: Player = players[message.from_user.id]
    chosen_category = message.text
    player.set_category(chosen_category)
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton('Готов!')]], resize_keyboard=True, one_time_keyboard=True)

    await bot.send_message(message.from_user.id, f'Итак, {player.name}, имя и вид деятельности теперь известны. Пора начать игру! \n\nТы готов?', reply_markup=keyboard)
    player.state = 'awaiting_game'


level1 = levels['level1']


@dp.message_handler(lambda message: players[message.from_user.id].state == 'awaiting_game')
async def game_begins(message: types.Message):
    player: Player = players[message.from_user.id]
    # Извлекаем данные из JSON
    title = level1['task1']['articles'][player.category]['title']
    link = level1['task1']['articles'][player.category]['link']

    keyboard = ReplyKeyboardMarkup([[KeyboardButton(
        'Прочел. К вопросам')]], resize_keyboard=True, one_time_keyboard=True)
    message_text = f'Первый уровень состоит из двух этапов \n\n1-й этап: \nПрочитать статью по выбранной категории {player.category}:\n\n[{title}]({link})'

    await bot.send_message(message.from_user.id, message_text, parse_mode="markdown")
    await bot.send_message(message.from_user.id, 'После прочтения, нажмите кнопку внизу, чтобы ответить на вопросы про статью.' +
                           '\nЕсли ваши правильные ответы составят выше 80%, вы проходите на следующий этап.', reply_markup=keyboard)
    player.state = 'reading_article'


@dp.message_handler(lambda message: players[message.from_user.id].state == 'reading_article')
async def questions_from_article(message: types.Message):
    player: Player = players[message.from_user.id]
    category = player.category
    player.correct_answers = 0  # Считаем правильные ответы
    player.question_number = 1  # Номер текущего вопроса
    await send_question(message.from_user.id, category, player.question_number)


async def send_question(user_id, category, question_number):
    # Получаем вопрос и варианты ответа
    question_data = level1['task1']['questions'][category][f'question{question_number}']
    question_text = question_data['text']
    options = question_data['options']
    random.shuffle(options)  # Перемешиваем ответы

    # Создаем кнопки с ответами
    keyboard = InlineKeyboardMarkup(row_width=1)
    for option in options:
        keyboard.add(InlineKeyboardButton(
            option, callback_data=f'answer_{option}'))

    await bot.send_message(user_id, question_text, reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data.startswith('answer_'))
async def process_answer(call: types.CallbackQuery):
    user_id = call.from_user.id
    player: Player = players[user_id]
    category = player.category
    question_number = player.question_number
    question_data = level1['task1']['questions'][category][f'question{question_number}']

    selected_answer = call.data.split('_')[1]
    correct_answer = question_data['correct']

    # Создаем сообщение с результатом
    keyboard = InlineKeyboardMarkup(row_width=1)
    for option in question_data['options']:
        if option == selected_answer:
            if option == correct_answer:
                text = f'{option} ✅'
            else:
                text = f'{option} ❌'
        else:
            text = option
        keyboard.add(InlineKeyboardButton(text, callback_data="none"))

    # Обновляем сообщение с результатом
    await call.message.edit_reply_markup(reply_markup=keyboard)

    # Проверяем правильность ответа
    if selected_answer == correct_answer:
        player.correct_answers += 1

    # Переход к следующему вопросу или завершение
    if player.question_number < 5:
        player.question_number += 1
        await send_question(user_id, category, player.question_number)
    else:
        if player.correct_answers >= 4:
            await bot.send_message(user_id, "Поздравляем! Вы прошли тест. Переходим к следующему этапу.")
            # Здесь будет логика для следующего этапа
        else:
            article = level1['task1']['articles'][player.category]
            await bot.send_message(user_id, f"К сожалению, вы ответили правильно на {player.correct_answers}/5 вопросов. Прочитайте статью еще раз.")
            await bot.send_message(user_id, f"[{article['title']}]({article['link']})", parse_mode="markdown", disable_web_page_preview=True)
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(
                "Прочитал. К вопросам", callback_data="restart_quiz"))
            await bot.send_message(user_id, "Нажмите кнопку ниже, чтобы начать тест заново.", reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data == "restart_quiz")
async def restart_quiz(call: types.CallbackQuery):
    user_id = call.from_user.id
    player: Player = players[user_id]
    player.correct_answers = 0  # Обнуляем счет правильных ответов
    player.question_number = 1  # Начинаем с первого вопроса
    await send_question(user_id, player.category, player.question_number)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
