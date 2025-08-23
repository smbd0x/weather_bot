from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.middlewares.services import ServicesMiddleware
from config import settings
from core.dto.user_dto import UserDTO
from core.services.message_service import MessageService
from core.services.user_service import UserService
from logger import bot_logger

admin_router = Router()
admin_router.message.middleware(ServicesMiddleware())


@admin_router.message(Command('get_user'))
async def start_command_handler(message: Message, user_service: UserService, message_service: MessageService):
    requested_user_id = message.text.replace('/get_user', '').strip()
    bot_logger.info('Вызов команды /get_user',
                    extra={'user_id': message.from_user.id, 'requested_user_id': requested_user_id})

    if message.from_user.id not in settings.admin_ids:
        bot_logger.warning('Вызов команды /get_user не от админа',
                           extra={'user_id': message.from_user.id, 'requested_user_id': requested_user_id})
        return

    try:
        requested_user_id = int(requested_user_id)
    except ValueError:
        bot_logger.info(f'Некорректный user_id',
                        extra={'user_id': message.from_user.id, 'requested_user_id': requested_user_id})
        await message.answer('Некорректный user_id')
        return

    user: UserDTO = await user_service.get_or_create_user(requested_user_id)

    text = message_service.get('ru.json', 'admin_get_user').format(**user.__dict__)
    await message.answer(text)
