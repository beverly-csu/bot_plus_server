import telebot
import requests
import keyboard

token = ""
URL = "http://127.0.0.1:5000/action/"
rus_cats = {
    "business": "Бизнес",
    "entertainment": "Развлечения",
    "general": "Популярное",
    "health": "Здоровье",
    "science": "Наука",
    "sports": "Спорт",
    "technology": "Технологии"
}

bot = telebot.TeleBot(token, parse_mode=None)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    exist = requests.get(URL + "user/getUser/" + str(chat_id)).json()
    print(exist)
    if exist["status"] == "error":
        create = requests.get(
            URL + f"user/createUser/{chat_id}&{message.from_user.first_name}&{message.from_user.last_name}").json()
        if create["status"] == "success":
            bot.send_message(chat_id,
                             (message.from_user.first_name + ", Вы успешно зарегистрировались в новостном боте!"))
        elif create["status"] == "error":
            bot.send_message(chat_id, (
                    message.from_user.first_name + ", к сожалению произошла ошибка. Свяжитесь с администратором."))
    elif exist["status"] == "ok":
        bot.send_message(chat_id, ("Я рад Вас видеть вновь, " + exist["name"] + "!"))


@bot.message_handler(func=lambda message: True)
def message_handler(message):
    chat_id = message.chat.id
    msg = message.text
    categories = requests.get(URL + f"user/getCategories/{chat_id}").json()
    user_info = requests.get(URL + f"user/getUser/{chat_id}").json()
    user_option = requests.get(URL + f"user/getUserOption/{chat_id}").json()
    if user_info["status"] == "error":
        send_welcome(message)
    else:
        for cat in rus_cats:
            if msg.startswith(rus_cats[cat]):
                requests.post(URL + f"user/setMenu/", {"menu_state": "category", "user_id": chat_id})
                requests.post(URL + f"user/setTempCat/", {"category": cat, "user_id": chat_id})
                cat_info = [cat]
                if categories[cat] == 1:
                    cat_info.append("Отписаться \u274C")
                elif categories[cat] == 0:
                    cat_info.append("Подписаться \u2705")
                bot.send_message(chat_id, "Тест", reply_markup=keyboard.category(chat_id, cat_info))
        numbers = ("1", "2", "3", "5")
        category = user_info["temp_cat"]
        temp_flag = user_info["temp_flag"]
        if temp_flag == "del":
            r = requests.post(URL + "user/delKey/", {"user_id": chat_id, "keyword": msg}).json()
            requests.post(URL + "user/setFlag/", {"user_id": chat_id, "flag": "none"})
            bot.send_message(chat_id, r["answer"])
        elif temp_flag == "add":
            r = requests.post(URL + "user/addKey/", {"user_id": chat_id, "keyword": msg}).json()
            requests.post(URL + "user/setFlag/", {"user_id": chat_id, "flag": "none"})
            bot.send_message(chat_id, r["answer"])
        elif msg == "Категории":
            requests.post(URL + f"user/setMenu/", {"menu_state": "categories", "user_id": chat_id})
            bot.send_message(chat_id, "Вы находитесь в меню выбора категорий!",
                             reply_markup=keyboard.categories(chat_id))
        elif msg.startswith("Новости по ключевым словам"):
            all_key_news(chat_id, user_option["pageSize"], user_option["language"])
        elif msg.startswith("Мои ключевые слова"):
            r = requests.get(URL + f"user/getKeys/{chat_id}").json()
            string = "Ваши ключевые слова:\n"
            for i in r["keywords"][0].split():
                string = string + i + "\n"
            bot.send_message(chat_id, string)
        elif msg == "Новости":
            all_news(chat_id, user_option["pageSize"], user_option["language"])
            all_key_news(chat_id, user_option["pageSize"], user_option["language"])
        elif msg.startswith("Подписаться"):
            cat_info = [category, "Отписаться \u274C"]
            r = requests.post(URL + "user/updateFollow/", {"category": category, "user_id": chat_id}).json()
            bot.send_message(chat_id, r["answer"], reply_markup=keyboard.category(chat_id, cat_info))
        elif msg.startswith("Отписаться"):
            cat_info = [category, "Подписаться \u2705"]
            r = requests.post(URL + "user/updateFollow/", {"category": category, "user_id": chat_id}).json()
            bot.send_message(chat_id, r["answer"], reply_markup=keyboard.category(chat_id, cat_info))
        elif msg.startswith("Новости категории"):
            data = {
                "count": user_option["pageSize"],
                "language": user_option["language"],
                "category": user_info["temp_cat"],
                "category_ru": rus_cats[user_info["temp_cat"]]
            }
            print_news(data, chat_id)
        elif msg.startswith("Настройки"):
            bot.send_message(chat_id, "Вы находитесь в меню настроек", reply_markup=keyboard.options())
            requests.post(URL + f"user/setMenu/", {"menu_state": "options", "user_id": chat_id})
        elif msg.startswith("Язык"):
            bot.send_message(chat_id, "Вы находитесь в меню выбора языка новостей", reply_markup=keyboard.language())
            requests.post(URL + f"user/setMenu/", {"menu_state": "language", "user_id": chat_id})
        elif msg == "\U0001F1F7 \U0001F1FA":
            r = requests.post(URL + "user/setOption/",
                              {"action": "setLanguage", "language": "ru", "user_id": chat_id}).json()
            bot.send_message(chat_id, r["answer"], reply_markup=keyboard.language())
        elif msg == "\U0001F1FA \U0001F1F8":
            r = requests.post(URL + "user/setOption/",
                              {"action": "setLanguage", "language": "en", "user_id": chat_id}).json()
            bot.send_message(chat_id, r["answer"], reply_markup=keyboard.language())
        elif msg.startswith("Количество"):
            bot.send_message(chat_id, "Выберите количество выводимых новостей из каждой категории",
                             reply_markup=keyboard.count(user_option["pageSize"]))
            requests.post(URL + f"user/setMenu/", {"menu_state": "count", "user_id": chat_id})
        elif msg.startswith("Мой аккаунт"):
            string = "Информация об аккаунте:\nID: " + str(user_info["user_id"]) + "\nИмя: " + user_info[
                "name"] + "\nФамилия: " + user_info["surname"] + "\nДата регистрации: " + user_info["date_reg"]
            bot.send_message(chat_id, string)
        elif msg.startswith(numbers):
            count = int(msg.replace("\u2705", ""))
            requests.post(URL + "user/setOption/",
                          {"action": "setCount", "count": count, "user_id": chat_id}).json()
            bot.send_message(chat_id, f"Количество выводимых новостей изменено на {count}",
                             reply_markup=keyboard.count(count))
        elif msg.startswith("Справка"):
            bot.send_message(chat_id, "<<Новостной бот>> был создан by beverly-csu")
        elif msg.startswith("Ключевые слова"):
            requests.post(URL + f"user/setMenu/", {"menu_state": "keys", "user_id": chat_id})
            bot.send_message(chat_id, "Вы находитесь в меню ключевых слов", reply_markup=keyboard.keywords())
        elif msg.startswith("Добавить"):
            requests.post(URL + "user/setFlag/", {"user_id": chat_id, "flag": "add"})
            bot.send_message(chat_id, "Введите слово для добавления")
        elif msg.startswith("Удалить"):
            requests.post(URL + "user/setFlag/", {"user_id": chat_id, "flag": "del"})
            bot.send_message(chat_id, "Введите слово для удаления")
        elif msg.startswith("Назад"):
            if user_info["menu_state"] == "categories":
                bot.send_message(chat_id, "Вы вернулись в главное меню", reply_markup=keyboard.main())
                requests.post(URL + f"user/setMenu/", {"menu_state": "main", "user_id": chat_id})
            elif user_info["menu_state"] == "category":
                bot.send_message(chat_id, "Вы вернулись в меню категорий", reply_markup=keyboard.categories(chat_id))
                requests.post(URL + f"user/setMenu/", {"menu_state": "categories", "user_id": chat_id})
            elif user_info["menu_state"] == "options":
                bot.send_message(chat_id, "Вы вернулись в главное меню", reply_markup=keyboard.main())
                requests.post(URL + f"user/setMenu/", {"menu_state": "main", "user_id": chat_id})
            elif user_info["menu_state"] == "language":
                bot.send_message(chat_id, "Вы вернулись в меню настроек", reply_markup=keyboard.options())
                requests.post(URL + f"user/setMenu/", {"menu_state": "options", "user_id": chat_id})
            elif user_info["menu_state"] == "count":
                bot.send_message(chat_id, "Вы вернулись в меню настроек", reply_markup=keyboard.options())
                requests.post(URL + f"user/setMenu/", {"menu_state": "options", "user_id": chat_id})
            elif user_info["menu_state"] == "keys":
                bot.send_message(chat_id, "Вы вернулись в главное меню", reply_markup=keyboard.main())
                requests.post(URL + f"user/setMenu/", {"menu_state": "main", "user_id": chat_id})


def all_news(chat_id, count, language):
    flag = False
    categories = requests.get(URL + f"user/getCategories/{chat_id}").json()
    for i in categories:
        if categories[i] == 1:
            flag = True
            data = {
                "count": count,
                "language": language,
                "category": i,
                "category_ru": rus_cats[i]
            }
            print_news(data, chat_id)
    if flag is False:
        bot.send_message(chat_id, "У вас нет активных подписок.")


def all_key_news(chat_id, count, language):
    keywords = requests.get(URL + f"user/getKeys/{chat_id}").json()
    if keywords["keywords"] is not None:
        for i in keywords["keywords"][0].split():
            data = {
                "count": count,
                "language": language,
                "keyword": i,
            }
            print_key_news(data, chat_id)
    else:
        bot.send_message(chat_id, "У вас нет активных подписок на ключевые слова.")


def print_news(data, user_id):
    request = URL + f"user/getNews/{data['category']}&{data['language']}&{data['count']}"
    news = requests.get(request).json()
    if news["status"] == "ok":
        bot.send_message(user_id, data["category_ru"])
        if news["totalResults"] < 3:
            data["count"] = news["totalResults"]
        for i in range(data["count"]):
            string = news["articles"][i]["title"] + "\n" + news["articles"][i]["url"]
            bot.send_message(user_id, string)
    else:
        bot.send_message(user_id, "Новостей по данной категории не найдено.")


def print_key_news(data, user_id):
    request = URL + f"user/getKeyNews/{data['keyword']}&{data['language']}&{data['count']}"
    news = requests.get(request).json()
    if news["status"] == "ok":
        bot.send_message(user_id, data["keyword"])
        if news["totalResults"] < 3:
            data["count"] = news["totalResults"]
        for i in range(data["count"]):
            string = news["articles"][i]["title"] + "\n" + news["articles"][i]["url"]
            bot.send_message(user_id, string)
    else:
        bot.send_message(user_id, "Новостей по данному ключевому слову не найдено.")


bot.polling()
