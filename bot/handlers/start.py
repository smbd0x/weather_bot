from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.keyboards.inline import main_keyboard
from bot.middlewares.services import ServicesMiddleware
from core.dto.user_dto import UserDTO
from core.services.message_service import MessageService
from core.services.user_service import UserService
from logger import bot_logger

start_router = Router()
start_router.message.middleware(ServicesMiddleware())


@start_router.message(Command('start'))
async def start_command_handler(message: Message, user_service: UserService, message_service: MessageService):
    bot_logger.info('Вызов команды /start', extra={'user_id': message.from_user.id})

    user: UserDTO = await user_service.get_or_create_user(message.from_user.id, message.from_user.username)

    text = message_service.get('ru.json', 'start').format(username=user.username or 'пользователь')
    await message.answer(text, reply_markup=main_keyboard())

