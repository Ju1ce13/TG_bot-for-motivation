from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from config import ADMIN_ID
from database.models.users import User


def trade(message_id: int) -> InlineKeyboardBuilder:
    """Create a trade keyboard with an optional admin menu."""
    builder = InlineKeyboardBuilder()
    if message_id == ADMIN_ID:
        builder = admin()
    builder.row(types.InlineKeyboardButton(text="Обменять", callback_data="trade"))
    return builder


def back_to_menu() -> InlineKeyboardBuilder:
    """Create a keyboard to return to the main menu."""
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Назад в профиль", callback_data="back"))
    return builder


def back_to_admin_menu() -> InlineKeyboardBuilder:
    """Create a keyboard to return to the admin menu."""
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Назад в админ_меню", callback_data="admin_back"))
    return builder


def admin() -> InlineKeyboardBuilder:
    """Create an admin menu keyboard."""
    builder = InlineKeyboardBuilder()
    actions = [
        "Просмотреть список юзеров", "Удалить пользователя", "Поставить дизлайк",
        "Пополнить баланс", "Изменить грейд", "Рассылка", "Обнулить дизлайки"
    ]
    for action in actions:
        builder.row(types.InlineKeyboardButton(text=action, callback_data=action))
    return builder


def create_user_keyboard(users: list[User], prefix: str) -> InlineKeyboardBuilder:
    """Create a keyboard with a list of users."""
    builder = InlineKeyboardBuilder()
    for user in users:
        builder.row(types.InlineKeyboardButton(text=user.name, callback_data=f"{prefix}_{user.id}"))
    return builder
