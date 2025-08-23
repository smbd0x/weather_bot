from aiogram import BaseMiddleware

from core.services.message_service import MessageService
from core.services.user_service import UserService
from core.services.weather_service import WeatherService
from sqlalchemy.ext.asyncio import AsyncSession

from data.database import async_session


class ServicesMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data: dict):
        data["user_service"] = UserService(async_session)
        data["weather_service"] = WeatherService()
        data["message_service"] = MessageService()
        return await handler(event, data)
