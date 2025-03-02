from aiogram import Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models.models import SessionLocal
from database.models.users import User
from database.utils.users import get_all_users, delete_user, get_user, get_user_by_id
from keyboards import admin, create_user_keyboard, back_to_admin_menu
from states import AllPath

router = Router()

@router.message(Command('admin_menu'))
async def admin_menu(message: types.Message):
    await message.delete()
    await message.answer("Выберите действие:", reply_markup=admin().as_markup())

@router.callback_query(F.data == "Удалить пользователя")
async def delete_user_handler(callback: types.CallbackQuery):
    with SessionLocal() as db:
        users = get_all_users(db)
        builder = create_user_keyboard(users, "delete")
        await callback.message.delete()
        await callback.message.answer("Выберите пользователя для удаления:", reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("delete_"))
async def handle_delete(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    with SessionLocal() as db:
        delete_user(db, user_id)
    await callback.message.delete()
    await callback.message.answer("Пользователь удален.")

# Command handlers
@router.message(Command('admin_menu'))
async def admin_menu(message: types.Message):
    """Handle the admin menu command."""
    await message.delete()
    await message.answer("Выберите действие:", reply_markup=admin().as_markup())

@router.callback_query(F.data == "admin_back")
async def admin_menu(callback: types.CallbackQuery):
    """Handle the back to admin menu callback."""
    await callback.message.delete()
    await callback.message.answer("Выберите действие:", reply_markup=admin().as_markup())


@router.callback_query(F.data == "Поставить дизлайк")
async def dislike_user(callback: types.CallbackQuery, state: FSMContext):
    """Handle the dislike user command."""
    with SessionLocal() as db:
        users = get_all_users(db)
        builder = create_user_keyboard(users, "dislike")
        await callback.message.delete()
        await state.set_state(AllPath.input_dislike)
        await callback.message.answer("Выберите пользователя для дизлайка:", reply_markup=builder.as_markup())

@router.callback_query(F.data == "Просмотреть список юзеров")
async def view_users(callback: types.CallbackQuery):
    """Handle the view users command."""
    with SessionLocal() as db:
        users = get_all_users(db)
        builder = create_user_keyboard(users, "view")
        await callback.message.delete()
        await callback.message.answer(
            "Выберите пользователя для просмотра информации:",
            reply_markup=builder.as_markup()
        )

@router.callback_query(F.data.startswith("view_"))
async def view_user_info(callback: types.CallbackQuery):
    """Handle the view user info callback."""
    user_id = int(callback.data.split("_")[1])
    with SessionLocal() as db:
        existing_user = get_user_by_id(db,user_id)
        print(user_id)
        await callback.message.delete()
        await callback.message.answer(
            f"Информация о пользователе: <a href='tg://user?id={existing_user.tg_id}'>{existing_user.name}</a>\n"
            f"Баланс: {existing_user.balance}\n"
            f"Дизлайки: {existing_user.dislikes}",
            parse_mode=ParseMode.HTML,
            reply_markup=back_to_admin_menu().as_markup()
        )

@router.callback_query(F.data == "Пополнить баланс")
async def top_up_balance(callback: types.CallbackQuery, state: FSMContext):
    """Handle the top-up balance command."""
    with SessionLocal() as db:
        users = get_all_users(db)
        builder = create_user_keyboard(users, "topup")
        await callback.message.delete()
        await state.set_state(AllPath.input_like)
        await callback.message.answer("Выберите пользователя для пополнения баланса:", reply_markup=builder.as_markup())

@router.callback_query(F.data == "Изменить грейд")
async def change_grade(callback: types.CallbackQuery):
    """Handle the change grade command."""
    with SessionLocal() as db:
        users = get_all_users(db)
        builder = create_user_keyboard(users, "change_grade")
        await callback.message.delete()
        await callback.message.answer("Выберите пользователя для изменения грейда:", reply_markup=builder.as_markup())

@router.callback_query(F.data == "Рассылка")
async def mailing(callback: types.CallbackQuery, state: FSMContext):
    """Handle the mailing command."""
    await callback.message.delete()
    await state.set_state(AllPath.post)
    await callback.message.answer("Напишите сообщение для рассылки:")

@router.callback_query(F.data == "Обнулить дизлайки")
async def reset_dislikes(callback: types.CallbackQuery):
    """Handle the reset dislikes command."""
    with SessionLocal() as db:
        users = get_all_users(db)
        for user in users:
            user.dislikes = 0
        db.commit()
    await callback.message.delete()
    await callback.message.answer("Дизлайки обнулены.", reply_markup=back_to_admin_menu().as_markup())

@router.message(AllPath.post)
async def send_mailing(message: types.Message, state: FSMContext):
    """Handle the mailing message."""
    with SessionLocal() as db:
        users = db.query(User).all()
        for user in users:
            await message.bot.copy_message(chat_id=user.tg_id, message_id=message.message_id, from_chat_id=message.from_user.id)
    await state.clear()
    await message.answer("Рассылка завершена.", reply_markup=back_to_admin_menu().as_markup())

@router.callback_query(F.data.startswith("delete_"))
async def handle_delete(callback: types.CallbackQuery):
    """Handle the delete user callback."""
    user_id = callback.data.split("_")[1]
    with SessionLocal() as db:
        existing_user = db.query(User).filter(User.id == user_id).first()
        db.delete(existing_user)
        db.commit()
    await callback.message.delete()
    await callback.message.answer("Пользователь удален.")

@router.callback_query(F.data.startswith("dislike_"))
async def handle_dislike(callback: types.CallbackQuery, state: FSMContext):
    """Handle the dislike callback."""
    user_id = callback.data.split("_")[1]
    await callback.message.answer("Введите число для выдачи дизлайков.")
    await state.update_data(user_id=user_id)

@router.message(AllPath.input_dislike)
async def handle_dislike(message: types.Message, state: FSMContext):
    """Handle the dislike input."""
    user_id = (await state.get_data())['user_id']
    with SessionLocal() as db:
        existing_user = db.query(User).filter(User.id == user_id).first()
        existing_user.dislikes += int(message.text)
        db.commit()
        await message.bot.send_message(chat_id=existing_user.tg_id, text=f"+{message.text} 👎")
    await state.clear()
    await message.delete()
    await message.answer("Дизлайки отправлены.", reply_markup=back_to_admin_menu().as_markup())

@router.callback_query(F.data.startswith("topup_"))
async def handle_topup(callback: types.CallbackQuery, state: FSMContext):
    """Handle the top-up callback."""
    user_id = callback.data.split("_")[1]
    await callback.message.answer("Введите число для пополнения баланса.")
    await state.update_data(user_id=user_id)

@router.message(AllPath.input_like)
async def handle_topup(message: types.Message, state: FSMContext):
    """Handle the top-up input."""
    user_id = (await state.get_data())['user_id']
    with SessionLocal() as db:
        existing_user = db.query(User).filter(User.id == user_id).first()
        existing_user.balance += int(message.text)
        db.commit()
        await message.bot.send_message(chat_id=existing_user.tg_id, text=f"+{message.text} 🔥")
    await state.clear()
    await message.delete()
    await message.answer("Баланс пополнен.", reply_markup=back_to_admin_menu().as_markup())

@router.callback_query(F.data.startswith("change_grade_"))
async def handle_change_grade(callback: types.CallbackQuery):
    """Handle the change grade callback."""
    user_id = callback.data.split("_")[2]
    builder = InlineKeyboardBuilder()
    grades = ["Джун", "Мидл", "Сеньор"]
    for index, grade in enumerate(grades):
        builder.row(types.InlineKeyboardButton(text=grade, callback_data=f"grade_{index + 1}_{user_id}"))
    await callback.message.delete()
    await callback.message.answer("Выберите новый грейд:", reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("grade_"))
async def handle_change_grade(callback: types.CallbackQuery):
    """Handle the grade selection callback."""
    grade = callback.data.split("_")[1]
    user_id = callback.data.split("_")[2]
    grades = {1: "Джун", 2: "Мидл", 3: "Сеньор"}
    with SessionLocal() as db:
        existing_user = db.query(User).filter(User.id == user_id).first()
        existing_user.grade = grades[int(grade)]
        db.commit()
        await callback.bot.send_message(chat_id=existing_user.tg_id, text=f"Вы получили новый грейд: {grades[int(grade)]}")
    await callback.message.delete()
    await callback.message.answer(f"Грейд изменен на {grades[int(grade)]}.", reply_markup=back_to_admin_menu().as_markup())



