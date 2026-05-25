from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_kr() -> ReplyKeyboardMarkup:
    buttons = [
        KeyboardButton(text="Get random verb"),
    ]
    return ReplyKeyboardMarkup(keyboard=[buttons], resize_keyboard=True)
