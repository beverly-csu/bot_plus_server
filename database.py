import sqlite3
import time
from flask import jsonify
import json

db_name = "db.sqlite"
connect = sqlite3.connect(db_name, check_same_thread=False)
cursor = connect.cursor()


def create():
    requests = [
        """CREATE TABLE IF NOT EXISTS "users" (
        "user_id" INTEGER NOT NULL UNIQUE,
        "name" TEXT,
        "surname" TEXT,
        "date_reg" INTEGER,
        "menu_state" TEXT NOT NULL DEFAULT "main",
        "temp_cat" TEXT,
        "temp_flag" TEXT,
        PRIMARY KEY("user_id"))""",
        """CREATE TABLE IF NOT EXISTS "keywords" (
        "user_id" INTEGER NOT NULL UNIQUE,
        "keywords" TEXT,
        PRIMARY KEY("user_id"))""",
        """CREATE TABLE IF NOT EXISTS "option" (
        "user_id" INTEGER NOT NULL UNIQUE,
        "pageSize" INTEGER NOT NULL DEFAULT 3,
        "language" TEXT NOT NULL DEFAULT "all",
        PRIMARY KEY("user_id"))""",
        """CREATE TABLE IF NOT EXISTS "categories" (
        "user_id" INTEGER NOT NULL UNIQUE,
        "business" INTEGER NOT NULL DEFAULT 0,
        "entertainment" INTEGER NOT NULL DEFAULT 0,
        "general" INTEGER NOT NULL DEFAULT 0,
        "health" INTEGER NOT NULL DEFAULT 0,
        "science" INTEGER NOT NULL DEFAULT 0,
        "sports" INTEGER NOT NULL DEFAULT 0,
        "technology" INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY("user_id"))"""
    ]
    for request in requests:
        cursor.execute(request)
    connect.commit()


def get_info(table):
    request = """SELECT * FROM {}""".format(table, )
    info = cursor.execute(request)
    info = info.fetchall()
    return info


def set_active_cat(user_id, category):
    request = """UPDATE "users" SET "temp_cat"="{}" WHERE "user_id"={}""".format(category, user_id)
    cursor.execute(request)
    connect.commit()


def update_follow(user_id, category):
    categories = cursor.execute("""SELECT * FROM "categories" WHERE "user_id"={}""".format(user_id)).fetchone()
    categories = {
        "business": categories[1],
        "entertainment": categories[2],
        "general": categories[3],
        "health": categories[4],
        "science": categories[5],
        "sports": categories[6],
        "technology": categories[7]
    }
    requests = [
        """UPDATE "categories" SET "{}"=1 WHERE "user_id"={}""".format(category, user_id),
        """UPDATE "categories" SET "{}"=0 WHERE "user_id"={}""".format(category, user_id),
    ]
    if categories[category] == 1:
        cursor.execute(requests[1])
        connect.commit()
        return {"status": "ok", "answer": "Вы отписались от данной категории."}
    else:
        cursor.execute(requests[0])
        connect.commit()
        return {"status": "ok", "answer": "Вы подписались на данную категорию."}


def get_user(user_id):
    request = """SELECT * FROM "users" WHERE "user_id"={}""".format(user_id)
    info = cursor.execute(request).fetchone()
    if info is None:
        info = {
            "status": "error"
        }
    else:
        info = {
            "status": "ok",
            "user_id": info[0],
            "name": info[1],
            "surname": info[2],
            "date_reg": info[3],
            "menu_state": info[4],
            "temp_cat": info[5],
            "temp_flag": info[6]
        }
    return jsonify(info)


def get_user_keywords(user_id):
    request = """SELECT * FROM "keywords" WHERE "user_id"={}""".format(user_id)
    info = cursor.execute(request).fetchone()
    if info is None:
        info = {
            "status": "error"
        }
    else:
        info = {
            "status": "ok",
            "user_id": info[0],
            "keywords": [info[1]],
        }
    return jsonify(info)


def add_keyword(user_id, keyword):
    keywords = cursor.execute("""SELECT * FROM "keywords" WHERE "user_id"={}""".format(user_id)).fetchone()
    keywords = keywords[1].split()
    for key in keywords:
        if key == keyword:
            return "Данное слово уже есть в вашем списке"
    keywords.append(keyword)
    keywords = str(keywords).replace("[", "")
    keywords = keywords.replace("]", "")
    keywords = keywords.replace("'", " ")
    keywords = keywords.replace(",", " ")
    keywords = keywords.replace(",", " ")
    cursor.execute("""UPDATE "keywords" SET "keywords"="{}" WHERE "user_id"={}""".format(keywords, user_id))
    connect.commit()
    return "Слово было успешно добавлено"


def del_keyword(user_id, keyword):
    keywords = cursor.execute("""SELECT * FROM "keywords" WHERE "user_id"={}""".format(user_id)).fetchone()
    keywords = keywords[1].split()
    try:
        keywords.pop(keywords.index(keyword))
    except ValueError:
        return "Данного слова нет в вашем списке"
    keywords = str(keywords).replace("[", "")
    keywords = keywords.replace("]", "")
    keywords = keywords.replace("'", " ")
    keywords = keywords.replace(",", " ")
    keywords = keywords.replace(",", " ")
    cursor.execute("""UPDATE "keywords" SET "keywords"="{}" WHERE "user_id"={}""".format(keywords, user_id))
    connect.commit()
    return "Слово было удалено из вашего списка"


def set_flag(user_id, flag):
    request = """UPDATE "users" SET "temp_flag"="{}" WHERE "user_id"={}""".format(flag, user_id)
    cursor.execute(request)
    connect.commit()


def get_user_option(user_id):
    request = """SELECT * FROM "option" WHERE "user_id"={}""".format(user_id)
    info = cursor.execute(request).fetchone()
    if info is None:
        info = {
            "status": "error"
        }
    else:
        info = {
            "status": "ok",
            "user_id": info[0],
            "language": info[2],
            "pageSize": info[1],
        }
    return jsonify(info)


def edit_user(data):
    request = """UPDATE "users" SET "name"="{}", "surname"="{}" WHERE "user_id"={}""".format(data["name"],
                                                                                             data["surname"],
                                                                                             data["user_id"])
    cursor.execute(request)
    connect.commit()


def delete_user(user_id):
    requests = [
        """DELETE FROM "users" WHERE "user_id"={}""".format(user_id),
        """DELETE FROM "option" WHERE "user_id"={}""".format(user_id),
        """DELETE FROM "categories" WHERE "user_id"={}""".format(user_id),
        """DELETE FROM "keywords" WHERE "user_id"={}""".format(user_id)
    ]
    for request in requests:
        cursor.execute(request)
    connect.commit()


def create_user(data):
    requests = [
        """INSERT INTO "users" ("user_id", "name", "surname", "date_reg") VALUES ({}, "{}", "{}", "{}")""".format(
            data["user_id"], data["name"], data["surname"], time.strftime("%x %X", time.localtime(time.time()))),
        """INSERT INTO "categories" ("user_id") VALUES ({})""".format(data["user_id"]),
        """INSERT INTO "keywords" ("user_id") VALUES ({})""".format(data["user_id"]),
        """INSERT INTO "option" ("user_id") VALUES ({})""".format(data["user_id"])
    ]
    try:
        for request in requests:
            cursor.execute(request)
        connect.commit()
        return jsonify({"status": "success"})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error"})


def set_option(action, value, user_id):
    request = ""
    if action == "setLanguage":
        request = """UPDATE "option" SET "language"="{}" WHERE "user_id"={}""".format(value, user_id)
    elif action == "setCount":
        request = """UPDATE "option" SET "pageSize"="{}" WHERE "user_id"={}""".format(value, user_id)
    cursor.execute(request)
    connect.commit()


def get_categories(user_id):
    request = """SELECT * FROM "categories" WHERE "user_id"={}""".format(user_id)
    info = cursor.execute(request).fetchone()
    if info is None:
        info = {
            "status": "error"
        }
    else:
        info = {
            "status": "ok",
            "business": info[1],
            "entertainment": info[2],
            "general": info[3],
            "health": info[4],
            "science": info[5],
            "sports": info[6],
            "technology": info[7]
        }
    return jsonify(info)


def set_menu(user_id, state):
    request = """UPDATE "users" SET "menu_state"="{}" WHERE "user_id"={}""".format(state, user_id)
    cursor.execute(request)
    connect.commit()
