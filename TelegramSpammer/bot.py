from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from asyncio import run
import logging
import nest_asyncio
nest_asyncio.apply()
import aiogram
from config import Config
import db
import send

logging.basicConfig(level=logging.INFO)
config = Config()

bot_help = """Справка по командам

Пример добавления групп в рассылку: /add_groups <ссылка_на_группу>
Пример удаления групп из рассылки: /delete_groups <ссылка_на_группу>
Пример добавления сообщения для рассылки: /set_message <ваше сообщение>

Символы <> ставить не надо!
"""

bot_commands = {
    '/start': 'Запуск бота/главное меню',
    '/add_groups': 'Добавить группы в рассылку',
    '/show_groups': 'Показать, какие группы сейчас в рассылке',
    '/set_message': 'Установить новый текст для рассылки',
    '/show_message': 'Показать текущий текст рассылки',
    '/send_all': 'Начать рассылку',
    '/delete_groups': 'Удалить группы из рассылки',
    '/help': 'Справка по командам'
}

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

    
@dp.message(Command("start"))
async def start(message: types.Message):
    answer_message = "Команды: \n\n" + \
                     '\n'.join([f'{com} : {bot_commands[com]}' for com in bot_commands.keys()]) + "\n\nПосмотрите справку!"
    await message.answer(answer_message)


@dp.message(Command("add_groups"))
async def add_groups(message: types.Message):
    args = message.text.split(maxsplit=1)

    if len(args) > 1:
        group_links = args[1]
        try:
            db.insert('links', group_links)
        except Exception as e:
            await message.answer(f"Не удалось записать группы.\nОшибка: {e}")
            return
        await message.answer("Группы были записаны.")
        await show_groups(message)
    else:
        await message.answer("Вы не написали группы!")


@dp.message(Command("show_groups"))
async def show_groups(message: types.Message):
    groups = db.getall('links')
    if groups:
        answer_message = "Группы для рассылки: \n\n" + \
                         '\n'.join([f"{index + 1}) {group}" for index, group in enumerate(groups)])
        await message.answer(answer_message)
    else:
        await message.answer("У вас пока нет групп для рассылки.\nВведите /add_groups, чтобы добавить их.")


@dp.message(Command("set_message"))
async def set_message(message: types.Message):
    args = message.text.split(maxsplit=1)

    if len(args) > 1:
        new_message = args[1]
        messages = db.getall('messages')

        try:
            if messages:
                db.update('messages', new_message)
                await message.answer("Сообщение было обновлено.")
            else:
                db.insert('messages', new_message)
                await message.answer("Сообщение было записано.")
        except Exception as e:
            await message.answer(f"Не удалось записать сообщение.\nОшибка: {e}")
    else:
        await message.answer("Вы не написали сообщение!")


@dp.message(Command("show_message"))
async def show_message(message: types.Message):
    messages = db.getall('messages')

    if messages and messages[0]:
        try:
            await message.answer(messages[0])
        except aiogram.utils.exceptions.MessageTextIsEmpty:
            await message.answer('Вы задали пустое сообщение!')
    else:
        await message.answer("У вас пока нет сообщения для рассылки.\nВведите /set_message, чтобы добавить его.")


@dp.message(Command("send_all"))
async def sendall(message: types.Message):
    groups = db.getall('links')
    text = db.getall('messages')

    if not text or not text[0]:
        await show_message(message)
        return

    if not groups:
        await show_groups(message)
        return

    error_message = await send.start(groups, text[0])

    if error_message:
        await message.answer(f'Рассылка прошла с ошибками.\n\n{error_message}.')
    else:
        await message.answer('Рассылка успешно проведена')


@dp.message(Command("delete_groups"))
async def delete_groups(message: types.Message):
    args = message.text.split(maxsplit=1)
    links_to_delete = args[1] if len(args) > 1 else None

    if links_to_delete:
        try:
            db.delete('links', links_to_delete)
            await message.answer('Группы были удалены.\n')
            await show_groups(message)
        except Exception as e:
            await message.answer(f'Не удалось удалить группы.\nОшибка: {e}')
    else:
        await message.answer("Вы не написали группы!")


@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(bot_help)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    run(main())
