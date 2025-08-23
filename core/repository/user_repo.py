from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from data.models import User
from logger import repo_logger


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, user_id: int) -> User | None:
        repo_logger.info(f'Получение пользователя', extra={'user_id': user_id})

        return await self.session.get(User, user_id)

    async def get_or_create_user(self, user_id: int, username: str | None = None) -> User:
        repo_logger.info(f'Создание или получение пользователя', extra={'user_id': user_id, 'username': username})

        user = await self.get_user(user_id)
        if user:
            repo_logger.info(f'Пользователь найден', extra={'user_id': user_id})
            return user
        repo_logger.info(f'Пользователь не найден', extra={'user_id': user_id, 'username': username})
        user = User(id=user_id, username=username, balance=0)
        self.session.add(user)
        await self.session.flush()
        repo_logger.info(f'Пользователь создан', extra={'user_id': user_id, 'username': username})
        return user

    async def get_all_users(self) -> Sequence[User]:
        repo_logger.info(f'Получение всех пользователей')

        query = select(User)
        res = await self.session.execute(query)
        return res.scalars().all()

    async def add_balance(self, user_id: int, amount: int) -> None:
        repo_logger.info(f'Изменение баланса на {amount}', extra={'user_id': user_id})

        user = await self.get_user(user_id)
        if user:
            user.balance += amount
