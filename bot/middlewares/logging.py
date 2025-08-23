from aiogram import BaseMiddleware
from logger import bot_logger


class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data: dict):
        try:
            return await handler(event, data)
        except Exception as e:
            user_id = getattr(event, "from_user", None)
            u_id = user_id.id if user_id else "-"
            bot_logger.exception(f"Ошибка при обработке события: {e}", extra={"user_id": u_id})
            raise
