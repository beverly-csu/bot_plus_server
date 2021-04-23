from telebot import types
import requests

URL = "http://127.0.0.1:5000/action/"


chars_in_cat = {
        "business": 'Новости категории "Бизнес \U0001F4C8"',
        "entertainment": 'Новости категории "Развлечения \U0001F52E"',
        "general": 'Новости категории "Популярное \U0001F3A7"',
        "health": 'Новости категории "Здоровье \U0001F489"',
        "science": 'Новости категории "Наука \U0001F52C"',
        "sports": 'Новости категории "Спорт \U0001F3C0"',
        "technology": 'Новости категории "Технологии \U0001F4F1"'
    }


def get_keyboard(keys):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for line in keys:
        keyboard.add(*[types.KeyboardButton(name) for name in line])
    return keyboard


def categories(user_id):
    follow_char = "\u2705"
    keys = [["Бизнес", "Развлечения"], ["Популярное", "Здоровье"], ["Наука", "Спорт"], ["Технологии", "Назад \u21A9"]]
    cats = requests.get(URL + f"user/getCategories/{user_id}").json()
    if cats["business"] == 1:
        keys[0][0] = keys[0][0] + " " + follow_char
    if cats["entertainment"] == 1:
        keys[0][1] = keys[0][1] + " " + follow_char
    if cats["general"] == 1:
        keys[1][0] = keys[1][0] + " " + follow_char
    if cats["health"] == 1:
        keys[1][1] = keys[1][1] + " " + follow_char
    if cats["science"] == 1:
        keys[2][0] = keys[2][0] + " " + follow_char
    if cats["sports"] == 1:
        keys[2][1] = keys[2][1] + " " + follow_char
    if cats["technology"] == 1:
        keys[3][0] = keys[3][0] + " " + follow_char
    return get_keyboard(keys)


def main():
    keys = [["Новости"], ["Категории", "Ключевые слова"], ["Настройки", "Справка"]]
    return get_keyboard(keys)


def options():
    keys = [["Язык", "Количество страниц"], ["Мой аккаунт", "Назад \u21A9"]]
    return get_keyboard(keys)


def language():
    keys = [["\U0001F1F7 \U0001F1FA", "\U0001F1FA \U0001F1F8", "Назад \u21A9"]]
    return get_keyboard(keys)


def count(page_size):
    keys = [["1", "2", "3", "5", "Назад \u21A9"]]
    follow_char = " \u2705"
    page_size = str(page_size)
    for size in keys[0]:
        if page_size == size:
            index = keys[0].index(size)
            keys[0][index] += follow_char
    return get_keyboard(keys)


def keywords():
    keys = [["Новости по ключевым словам"], ["Мои ключевые слова"], ["Добавить", "Удалить", "Назад \u21A9"]]
    return get_keyboard(keys)


def category(user_id, cat_info):
    keys = [[chars_in_cat[cat_info[0]]], [cat_info[1], "Назад \u21A9"]]
    return get_keyboard(keys)
