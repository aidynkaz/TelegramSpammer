from telethon import TelegramClient
import logging
from config import Config
from typing import Dict, Iterable


config = Config()

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

client = TelegramClient('script', api_id=config.API_ID, api_hash=config.API_HASH)

async def sendall(groups : Iterable[str], message_text : str) -> Dict:

    """Send specified message text to specified groups
    Also collect exceptions in the process 
    and return dict with {group, where exception was raised : exception message} key-values"""

    errors = {}
    for group in groups:
        try:
            await client.send_message(group, message_text)
        except Exception as e:
            errors[f'{group}'] = str(e)
    return errors

async def create_error_message(errors : Dict) -> str:

    """Collects exceptions from erros dict into 1 error message"""

    answer_message = ''
    for i, (error_group, error_message) in enumerate(errors.items()):
        answer_message += f"Не удалось отправить сообщение в группу {error_group}\n"\
                   f"Ошибка: {error_message}\n\n"

    return answer_message

async def start(groups : Iterable[str], message_text : str) -> str:

    """Starts spam process and returns error message"""

    async with client:
        errors = client.loop.run_until_complete(sendall(groups, message_text))
        return await create_error_message(errors)
