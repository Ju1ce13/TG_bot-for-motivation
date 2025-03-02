from aiogram import Router, types, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext

from database.models.models import SessionLocal
from database.utils.users import get_user, create_user
from keyboards import trade
from states import AllPath

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    with SessionLocal() as db:
        existing_user = get_user(db, message.from_user.id)
        if existing_user:
            await message.answer(
                f"Добро пожаловать, {existing_user.name}!\n"
                f"Твой грейд: {existing_user.grade}\n"
                f"У тебя: 🔥{existing_user.balance}!\n"
                f"А также {existing_user.dislikes}👎",
                reply_markup=trade(message.chat.id).as_markup())
        else:
            await message.answer("Добро пожаловать! Пожалуйста, зарегистрируйтесь.")
            await message.answer("Введите ваше имя:")
            await state.set_state(AllPath.registration)

@router.message(StateFilter(AllPath.registration), F.text)
async def cmd_start(message: types.Message, state: FSMContext):
    with SessionLocal() as db:
        new_user = create_user(db, message.text, message.from_user.id)
    await message.answer(f"Вы успешно зарегистрированы: {message.text}")
    await message.delete()
    await message.answer(
        f"Добро пожаловать, {new_user.name}!\n"
        f"Твой грейд: {new_user.grade}\n"
        f"У тебя: 🔥{new_user.balance}!\n"
        f"А также {new_user.dislikes}👎",
        reply_markup=trade(message.chat.id).as_markup())
    await state.set_state(AllPath.choosing_option)