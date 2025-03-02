from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import ADMIN_ID
from database.models.models import SessionLocal
from database.utils.users import get_user
from keyboards import back_to_menu, trade
from states import AllPath

router = Router()

# Список товаров для обмена
TRADE_OPTIONS = [
    {"name": "Убрать дизлайк", "cost": 2, "callback": "option_0"},
    {"name": "Купить кофе", "cost": 11, "callback": "option_1"},
    {"name": "Яндекс Плюс (1 месяц)", "cost": 25, "callback": "option_2"},
    {"name": "Секретный приз", "cost": 50, "callback": "option_3"},
    {"name": "Обед до 500 рублей", "cost": 55, "callback": "option_4"},
    {"name": "Сертификат в ЗЯ за 1000 рублей", "cost": 75, "callback": "option_5"},
    {"name": "Телеграмм премиум (3 месяца)", "cost": 100, "callback": "option_6"},
]

@router.callback_query(F.data == "trade")
async def show_trade_options(callback: types.CallbackQuery):
    """Show trade options to the user."""
    builder = InlineKeyboardBuilder()
    for index, option in enumerate(TRADE_OPTIONS):
        builder.row(types.InlineKeyboardButton(
            text=f"{option['name']} {option['cost']}🔥",
            callback_data=option['callback']
        ))
    builder.row(types.InlineKeyboardButton(
        text="Назад в профиль", callback_data="back"
    ))

    with SessionLocal() as db:
        user = get_user(db, callback.from_user.id)
        await callback.message.delete()
        await callback.message.answer(
            f"Выбери товар\nТвой баланс: {user.balance}🔥",
            reply_markup=builder.as_markup(),
        )

@router.callback_query(F.data.startswith("option_"))
async def confirm_trade_option(callback: types.CallbackQuery):
    """Ask the user to confirm the selected trade option."""
    option_index = int(callback.data.split("_")[1])
    option = TRADE_OPTIONS[option_index]

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="Да", callback_data=f"confirm_purchase_{option_index}"
    ))
    builder.row(types.InlineKeyboardButton(
        text="Нет", callback_data="cancel_purchase"
    ))

    await callback.message.delete()
    await callback.message.answer(
        f"Ты выбираешь: {option['name']}\nЦена: {option['cost']}🔥\nТы уверен/а в своем выборе?",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data.startswith("confirm_purchase_"))
async def process_purchase(callback: types.CallbackQuery):
    """Process the purchase of a trade option."""
    option_index = int(callback.data.split("_")[2])
    option = TRADE_OPTIONS[option_index]

    with SessionLocal() as db:
        user = get_user(db, callback.from_user.id)
        if user.balance >= option['cost']:
            user.balance -= option['cost']
            if option_index == 0:  # Убрать дизлайк
                if user.dislikes > 0:
                    user.dislikes -= 1
                else:
                    await callback.message.answer("У вас нет дизлайков.")
                    return
            db.commit()
            await callback.message.delete()
            await callback.message.answer(
                f"Покупка совершена. Ваш новый баланс: {user.balance}🔥",
                reply_markup=back_to_menu().as_markup()
            )
            # Уведомление админу
            await callback.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"{user.name} обменял {option['name']} за {option['cost']}🔥"
            )
        else:
            await callback.message.answer("Недостаточно средств на счете.")

@router.callback_query(F.data.startswith("back"))
async def cmd_back(callback: types.CallbackQuery, state: FSMContext):
    """Handle the back to profile callback."""
    with SessionLocal() as db:
        existing_user = get_user(db, callback.from_user.id)
        if existing_user:
            await callback.message.answer(
                f"Добро пожаловать, {existing_user.name}!\n"
                f"Твой грейд: {existing_user.grade}\n"
                f"У тебя: 🔥{existing_user.balance}!\n"
                f"А также {existing_user.dislikes}👎",
                reply_markup=trade(callback.message.chat.id).as_markup())
        else:
            await callback.message.answer("Добро пожаловать! Пожалуйста, зарегистрируйтесь.")
            await callback.message.answer("Введите ваше имя:")
            await state.set_state(AllPath.registration)

@router.callback_query(F.data == "cancel_purchase")
async def cancel_purchase(callback: types.CallbackQuery):
    """Cancel the purchase and return to the trade menu."""
    await callback.message.delete()
    await callback.message.answer("Покупка отменена.", reply_markup=back_to_menu().as_markup())