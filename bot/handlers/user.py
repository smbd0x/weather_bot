from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import LabeledPrice, PreCheckoutQuery, Message, CallbackQuery

from bot.keyboards.inline import balance_keyboard, cancel_keyboard
from bot.middlewares.services import ServicesMiddleware
from bot.states.payment import PaymentStates
from config import settings
from core.dto.user_dto import UserDTO
from core.services.message_service import MessageService
from core.services.user_service import UserService
from core.services.weather_service import WeatherService
from logger import bot_logger

user_router = Router()
user_router.message.middleware(ServicesMiddleware())
user_router.callback_query.middleware(ServicesMiddleware())


@user_router.message(StateFilter(None), F.content_type == 'location')
async def location_handler(message: Message, weather_service: WeatherService, user_service: UserService,
                           message_service: MessageService):
    bot_logger.info('Получена геометка от пользователя', extra={'user_id': message.from_user.id})

    lat = message.location.latitude
    lon = message.location.longitude

    user: UserDTO = await user_service.get_or_create_user(message.from_user.id)

    try:
        weather = await weather_service.get_weather_for_user(lat, lon, user, user_service)
    except ValueError as e:
        await message.answer(str(e))
        return

    text = message_service.get('ru.json', 'weather').format(temperature=weather.current_weather.temperature,
                                                            windspeed=weather.current_weather.windspeed,
                                                            weathercode=weather.current_weather.weathercode)
    await message.answer(text)


@user_router.callback_query(F.data == 'balance')
async def balance_button_handler(call: CallbackQuery, user_service: UserService, message_service: MessageService):
    bot_logger.info('Нажатие кнопки "Баланс"', extra={'user_id': call.from_user.id})

    user: UserDTO = await user_service.get_or_create_user(call.from_user.id)

    text = message_service.get('ru.json', 'balance').format(user_id=user.id, balance=user.balance)
    await call.message.answer(text, reply_markup=balance_keyboard())
    await call.answer()


@user_router.callback_query(F.data == 'add_balance')
async def balance_button_handler(call: CallbackQuery, message_service: MessageService, state: FSMContext):
    bot_logger.info('Нажатие кнопки "Пополнить баланс"', extra={'user_id': call.from_user.id})

    await state.set_state(PaymentStates.waiting_for_amount)

    text = message_service.get('ru.json', 'payment_amount_input')
    await call.message.answer(text, reply_markup=cancel_keyboard())
    await call.answer()


@user_router.message(StateFilter(PaymentStates.waiting_for_amount), F.text)
async def balance_button_handler(message: Message, message_service: MessageService, state: FSMContext):
    bot_logger.info(f'Пользователь ввел сумму: {message.text}',
                    extra={'user_id': message.from_user.id, 'amount': message.text})

    try:
        amount = int(message.text)
    except ValueError:
        bot_logger.info(f'Некорректная сумма',
                        extra={'user_id': message.from_user.id, 'amount': message.text})
        text = message_service.get('ru.json', 'payment_amount_error')
        await message.answer(text, reply_markup=cancel_keyboard())
        return

    prices = [LabeledPrice(label='Пополнение баланса', amount=amount * 100)]  # в копейках

    await message.answer_invoice(
        title='Пополнение баланса',
        description='Тестовое пополнение',
        provider_token=settings.provider_token,
        currency='RUB',
        prices=prices,
        start_parameter='topup',
        payload=str(message.from_user.id)
    )

    await state.clear()


@user_router.pre_checkout_query()
async def pre_checkout(pre_checkout_q: PreCheckoutQuery):
    await pre_checkout_q.answer(ok=True)


@user_router.message(F.successful_payment)
async def successful_payment_handler(message: Message, user_service: UserService, message_service: MessageService):
    bot_logger.info(f'Платеж удачно проведен',
                    extra={'user_id': message.from_user.id, 'amount': message.successful_payment.total_amount // 100})

    amount_rub = message.successful_payment.total_amount // 100
    await user_service.add_balance(message.from_user.id, amount_rub)

    text = message_service.get('ru.json', 'successful_payment').format(amount=amount_rub)
    await message.reply(text)


@user_router.callback_query(F.data == 'cancel')
async def cancel_button_handler(call: CallbackQuery, state: FSMContext, message_service: MessageService):
    bot_logger.info('Нажатие кнопки "Отмена"', extra={'user_id': call.from_user.id})

    await call.message.delete()
    await state.clear()

    text = message_service.get('ru.json', 'cancel')
    await call.message.answer(text)
    await call.answer()
