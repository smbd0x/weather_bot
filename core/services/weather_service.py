import httpx
import json

from httpx import RequestError, HTTPStatusError
from core.dto.user_dto import UserDTO
from core.dto.weather_dto import WeatherDTO
from core.services.user_service import UserService
from infrastructure.redis_client import get_redis
from config import settings
from logger import service_logger

COST_PER_WEATHER = 5


class WeatherService:
    def __init__(self):
        self.forecast_url = settings.weather_api_url

    async def _get_weather(self, lat: float, lon: float) -> WeatherDTO:
        service_logger.info('Получение погоды', extra={'lat': lat, 'lon': lon})

        redis = await get_redis()
        cache_key = f'weather:la{str(lat)}_lo{str(lon)}'

        if (cached := await redis.get(cache_key)) is not None:
            service_logger.info('Есть актуальный кэш, погода получена', extra={'lat': lat, 'lon': lon})
            return json.loads(cached)

        try:
            async with httpx.AsyncClient() as client:
                service_logger.info('Отправка запроса к WEATHER_API', extra={'lat': lat, 'lon': lon})
                r = await client.get(self.forecast_url,
                                     params={'latitude': lat, 'longitude': lon, 'current_weather': True}, timeout=10)
                r.raise_for_status()
                data = r.json()
                service_logger.info('Погода получена', extra={'lat': lat, 'lon': lon})
        except HTTPStatusError as e:
            service_logger.exception(f'Ошибка при обращении к WEATHER_API: {e}', extra={'lat': lat, 'lon': lon})
            raise ValueError('Ошибка при обращении к погодному API. Попробуйте позже.')
        except RequestError:
            raise ValueError('Ошибка при обращении к погодному API. Попробуйте позже.')

        await redis.setex(cache_key, 60, json.dumps(data))
        service_logger.info('Кэш погоды обновлен', extra={'lat': lat, 'lon': lon})

        try:
            weather_dto = WeatherDTO.parse_obj(data)
        except Exception as e:
            service_logger.exception(f'Некорректные данные от WEATHER_API: {e}',
                                     extra={'lat': lat, 'lon': lon, 'data': data})
            raise ValueError(f'Некорректные данные от API')

        return weather_dto

    async def get_weather_for_user(self, lat: float, lon: float, user: UserDTO,
                                   user_service: UserService) -> WeatherDTO:
        service_logger.info('Получение погоды для пользователя', extra={'user_id': user.id, 'lat': lat, 'lon': lon})

        if user.balance < COST_PER_WEATHER:
            service_logger.info(
                'Недостаточно средств для запроса погоды',
                extra={'user_id': user.id, 'required_balance': COST_PER_WEATHER, 'current_balance': user.balance}
            )
            raise ValueError(f'Недостаточно средств\nБаланс: {user.balance} ₽\nНужно: {COST_PER_WEATHER} ₽')

        weather = await self._get_weather(lat, lon)

        await user_service.add_balance(user.id, -COST_PER_WEATHER)

        return weather
