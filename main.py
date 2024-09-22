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
    keyboard = ReplyKeyboardMarkup([[KeyboardButton("Да, начнем!")]],
                                   resize_keyboard=True,
                                   one_time_keyboard=True)
    await bot.send_message(message.from_user.id,
                           hello_text,
                           reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Да, начнем!")
async def ask_name(message: types.Message):
    await bot.send_message(message.from_user.id, "Как тебя зовут?")
    # Устанавливаем состояние "ожидания имени"
    players[message.from_user.id].state = "awaiting_name"


@dp.message_handler(
    lambda message: players[message.from_user.id].state == 'awaiting_name')
async def choose_category(message: types.Message):
    player: Player = players[message.from_user.id]
    player.set_name(message.text)

    category_text = f"_Приятно познакомиться,_ *{player.name}*!\n\nВыбери категорию, которая наиболее близка к твоей деятельности:\n\n"
    science = KeyboardButton('Наука')
    art = KeyboardButton('Искусство')
    health = KeyboardButton('Медицина')
    sport = KeyboardButton('Спорт')
    it = KeyboardButton('IT')
    business = KeyboardButton('Бизнес')
    keyboard = ReplyKeyboardMarkup(one_time_keyboard=True,
                                   resize_keyboard=True)
    keyboard.add(it, science, business)
    keyboard.add(sport, health, art)

    # Отправляем пользователю описания категорий
    # await bot.send_message(message.from_user.id,
    #                        category_text,
    #
    #                        parse_mode='markdown')
    all_categories = ''
    number = 1
    for category, data in categories.items():
        description = data['description']
        all_categories += f"*{number}. {category}:*\n{description}\n\n"
        number += 1
    await bot.send_message(message.from_user.id,
                           category_text + all_categories,
                           reply_markup=keyboard,
                           parse_mode='markdown')

    player.state = 'awaiting_category'


@dp.message_handler(
    lambda message: players[message.from_user.id].state == 'awaiting_category')
async def perform_task(message: types.Message):
    player: Player = players[message.from_user.id]
    chosen_category = message.text
    player.set_category(chosen_category)
    keyboard = ReplyKeyboardMarkup([[KeyboardButton('Готов!')]],
                                   resize_keyboard=True,
                                   one_time_keyboard=True)

    await bot.send_message(
        message.from_user.id,
        f'Итак, {player.name}, имя и вид деятельности теперь известны. Пора начать игру! \n\nТы готов?',
        reply_markup=keyboard)
    player.state = 'awaiting_game'


level1 = levels['level1']


@dp.message_handler(
    lambda message: players[message.from_user.id].state == 'awaiting_game')
async def game_begins(message: types.Message):
    player: Player = players[message.from_user.id]
    # Извлекаем данные из JSON
    title = level1['task1']['articles'][player.category]['title']
    link = level1['task1']['articles'][player.category]['link']

    keyboard = ReplyKeyboardMarkup([[KeyboardButton('Прочел. К вопросам')]],
                                   resize_keyboard=True,
                                   one_time_keyboard=True)
    message_text = f'Первый уровень состоит из двух этапов \n\n1-й этап: \nПрочитать статью по выбранной категории {player.category}:\n\n[{title}]({link})'

    await bot.send_message(message.from_user.id,
                           message_text,
                           parse_mode="markdown")
    await bot.send_message(
        message.from_user.id,
        'После прочтения, нажмите кнопку внизу, чтобы ответить на вопросы про статью.'
        +
        '\nЕсли ваши правильные ответы составят выше 80%, вы проходите на следующий этап.',
        reply_markup=keyboard)
    player.state = 'reading_article'


@dp.message_handler(
    lambda message: players[message.from_user.id].state == 'reading_article')
async def questions_from_article(message: types.Message):
    player: Player = players[message.from_user.id]
    category = player.category
    player.correct_answers = 0  # Считаем правильные ответы
    player.question_number = 1  # Номер текущего вопроса
    await send_question(message.from_user.id, category, player.question_number)


async def send_question(user_id, category, question_number):
    # Получаем вопрос и варианты ответа
    question_data = level1['task1']['questions'][category][
        f'question{question_number}']
    question_text = question_data['text']
    options = question_data['options']
    random.shuffle(options)  # Перемешиваем ответы

    # Создаем кнопки с ответами
    keyboard = InlineKeyboardMarkup(row_width=1)
    for option in options:
        keyboard.add(
            InlineKeyboardButton(option, callback_data=f'answer_{option}'))

    await bot.send_message(user_id, question_text, reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data.startswith('answer_'))
async def process_answer(call: types.CallbackQuery):
    user_id = call.from_user.id
    player: Player = players[user_id]
    category = player.category
    question_number = player.question_number
    question_data = level1['task1']['questions'][category][
        f'question{question_number}']

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
            # await bot.send_message(user_id, "Поздравляем! Вы прошли тест.")
            # Здесь будет логика для следующего этапа
            book = level1['task2']['books'][category]
            book_title = book['title']
            book_link = book['link']

            # Формируем сообщение с гиперссылкой на книгу
            book_message = f"*Поздравляем! Ты прошел тест.*\n\nТеперь ты переходишь ко второму этапу! Для этого прочитай книгу: [{book_title}]({book_link}).\n\nПрочитай первые 20 страниц (предисловие не считается). Как только ты будешь готов, нажми на кнопку внизу, чтобы пройти тест по прочитанному материалу."

            # Кнопка для перехода к вопросам после прочтения
            keyboard = ReplyKeyboardMarkup(
                [[KeyboardButton('Прочитал. Готов к вопросам')]],
                resize_keyboard=True,
                one_time_keyboard=True)

            await bot.send_message(user_id,
                                   book_message,
                                   parse_mode="markdown",
                                   reply_markup=keyboard)

            # Устанавливаем новое состояние
            player.state = 'awaiting_book_questions'
        else:
            article = level1['task1']['articles'][player.category]
            await bot.send_message(
                user_id,
                f"К сожалению, вы ответили правильно на {player.correct_answers}/5 вопросов. Прочитайте статью еще раз."
            )
            await bot.send_message(user_id,
                                   f"[{article['title']}]({article['link']})",
                                   parse_mode="markdown",
                                   disable_web_page_preview=True)
            keyboard = InlineKeyboardMarkup()
            keyboard.add(
                InlineKeyboardButton("Прочитал. К вопросам",
                                     callback_data="restart_quiz"))
            await bot.send_message(
                user_id,
                "Нажмите кнопку ниже, чтобы начать тест заново.",
                reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data == "restart_quiz")
async def restart_quiz(call: types.CallbackQuery):
    user_id = call.from_user.id
    player: Player = players[user_id]
    player.correct_answers = 0  # Обнуляем счет правильных ответов
    player.question_number = 1  # Начинаем с первого вопроса
    await send_question(user_id, player.category, player.question_number)


@dp.message_handler(lambda message: players[message.from_user.id].state ==
                    'awaiting_book_questions')
async def ask_book_questions(message: types.Message):
    player: Player = players[message.from_user.id]
    category = player.category

    # Вопросы по книге из JSON (создаешь отдельные вопросы по каждому разделу)
    questions = level1['task2']['questions'][category]
    player.question_number = 1
    player.correct_answers = 0

    # Отправляем первый вопрос
    await send_book_question(message.from_user.id, category,
                             player.question_number)
    player.state = 'book_question_answering'


async def send_book_question(user_id, category, question_number):
    # Достаем вопрос
    question = level1['task2']['questions'][category][
        f'question{question_number + 1}']
    question_text = question['text']
    options = question['options']

    # Создаем Inline-кнопки с ответами (рандомный порядок)
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton(option, callback_data=f"b_answer:{option}")
        for option in options
    ]
    random.shuffle(buttons)
    keyboard.add(*buttons)

    # Отправляем вопрос
    await bot.send_message(user_id, question_text, reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('b_answer:'))
async def process_book_answer(callback_query: types.CallbackQuery):
    player: Player = players[callback_query.from_user.id]
    category = player.category
    question_number = player.question_number
    question_data = level1['task1']['questions'][category][
        f'question{question_number}']
    selected_answer = callback_query.data.split(":")[1]

    # Достаем правильный ответ
    correct_answer = level1['task2']['questions'][category][
        f'question{question_number + 1}']['correct']

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
    # Редактируем сообщение, чтобы показать правильные ответы
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)

    # Проверка на конец вопросов
    player.question_number += 1
    if player.question_number >= len(level1['task2']['questions'][category]):
        if player.correct_answers >= 4:
            await bot.send_message(
                callback_query.from_user.id,
                "Поздравляем! Вы прошли тест. Переходим к следующему уровню.")
            await bot.send_message(callback_query.from_user.id,
                                   "_Второй уровень на стадии подготовки_",
                                   parse_mode="markdown")
            # Здесь будет логика для следующего этапа
        else:
            await bot.send_message(
                callback_query.from_user.id,
                f"К сожалению, вы ответили правильно только на {player.correct_answers} из {player.question_number} вопросов. Прочитайте еще раз и попробуйте снова."
            )
            # Повтор тестирования
            player.state = 'awaiting_book_questions'
    else:
        # Отправляем следующий вопрос
        await send_book_question(callback_query.from_user.id, category,
                                 player.question_number)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
