from typing import List

from core.dto.user_dto import UserDTO
from core.repository.user_repo import UserRepository

from logger import service_logger


class UserService:

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def get_or_create_user(self, user_id: int, username: str | None = None) -> UserDTO:
        service_logger.info(f'Создание или получение пользователя', extra={'user_id': user_id, 'username': username})
        
        async with self.session_factory() as session:
            repo = UserRepository(session)
            user = await repo.get_or_create_user(user_id, username)
            await session.commit()
            service_logger.info(f'Commit: Создание или получение пользователя',
                                extra={'user_id': user_id, 'username': username})
            return UserDTO.from_orm(user)

    async def get_all_users(self) -> List[UserDTO]:
        service_logger.info(f'Получение всех пользователей')
        
        async with self.session_factory() as session:
            repo = UserRepository(session)
            res = await repo.get_all_users()
            return [UserDTO.from_orm(user) for user in res]

    async def add_balance(self, user_id: int, amount: int):
        service_logger.info(f'Изменение баланса на {amount}', extra={'user_id': user_id, 'amount': amount})
        
        async with self.session_factory() as session:
            repo = UserRepository(session)
            await repo.add_balance(user_id, amount)
            await session.commit()
            service_logger.info(f'Commit: Баланс изменен на {amount}', extra={'user_id': user_id, 'amount': amount})
