from flask import Flask, render_template, jsonify, request
import database as db
from newsapi import NewsApiClient

app = Flask(__name__)

news_api = NewsApiClient(api_key='a89e3f8f18c943ddbbc522a351aed79c')
cats = ["business", "entertainment", "general", "health", "science", "sports", "technology"]

db.create()


@app.route('/')
def start_page():
    return "TEST"


@app.route('/action/user/getUser/<user_id>')
def get_user(user_id):
    return db.get_user(user_id)


@app.route('/action/user/createUser/<user_id>&<name>&<surname>')
def create_user(user_id, name, surname):
    data = {
        "user_id": user_id,
        "name": name,
        "surname": surname
    }
    return db.create_user(data)


@app.route('/action/user/getCategories/<user_id>')
def get_categories(user_id):
    return db.get_categories(user_id)


@app.route('/action/user/getUserOption/<user_id>')
def get_user_option(user_id):
    return db.get_user_option(user_id)


@app.route('/action/user/setOption/', methods=['POST', 'GET'])
def set_option():
    if request.method == 'POST':
        action = request.form.get("action")
        user_id = request.form.get("user_id")
        if action == "setLanguage":
            language = request.form.get("language")
            db.set_option(action, language, user_id)
            lang = ""
            if language == "ru":
                lang = "русский"
            elif language == "en":
                lang = "английский"
            return jsonify({"status": "ok", "answer": f"Язык успешно изменен на {lang}"})
        if action == "setCount":
            count = request.form.get("count")
            print(type(count))
            db.set_option(action, count, user_id)
            return jsonify({"status": "ok", "answer": "Количество выводимых новостей успешно изменено"})


@app.route('/action/user/getNews/<category>&<language>&<page_size>')
def get_news(category, language, page_size):
    news = news_api.get_top_headlines(category=category,
                                      language=language,
                                      page_size=int(page_size))
    return news


@app.route('/action/user/getKeyNews/<keyword>&<language>&<page_size>')
def get_key_news(keyword, language, page_size):
    news = news_api.get_top_headlines(q=keyword,
                                      language=language,
                                      page_size=int(page_size))
    return news


@app.route('/action/user/getKeys/<user_id>')
def get_user_keywords(user_id):
    return db.get_user_keywords(user_id)


@app.route('/action/user/setMenu/', methods=['POST'])
def set_menu_state():
    if request.method == 'POST':
        state = request.form.get("menu_state")
        user_id = request.form.get("user_id")
        db.set_menu(user_id, state)
    return "Ok"


@app.route('/action/user/addKey/', methods=['POST'])
def add_keyword():
    if request.method == 'POST':
        keyword = request.form.get("keyword")
        user_id = request.form.get("user_id")
        return jsonify({"answer": db.add_keyword(user_id, keyword)})


@app.route('/action/user/delKey/', methods=['POST'])
def del_keyword():
    if request.method == 'POST':
        keyword = request.form.get("keyword")
        user_id = request.form.get("user_id")
        return jsonify({"answer": db.del_keyword(user_id, keyword)})


@app.route('/action/user/setFlag/', methods=['POST'])
def set_flag():
    if request.method == 'POST':
        flag = request.form.get("flag")
        user_id = request.form.get("user_id")
        db.set_flag(user_id, flag)
    return "Ok"


@app.route('/action/user/setTempCat/', methods=['POST'])
def set_temp_cat():
    if request.method == 'POST':
        category = request.form.get("category")
        user_id = request.form.get("user_id")
        db.set_active_cat(user_id, category)
    return "Ok"


@app.route('/action/user/updateFollow/', methods=['POST', 'GET'])
def update_follow():
    if request.method == 'POST':
        category = request.form.get("category")
        user_id = request.form.get("user_id")
        return db.update_follow(user_id, category)


@app.route('/users', methods=['GET', 'POST'])
def users_page():
    if request.method == 'GET':
        users = db.get_info("users")
        return render_template("users.html", users=users)
    elif request.method == 'POST':
        if request.form.get("action") == "edit":
            data = {
                "user_id": request.form.get("user_id"),
                "name": request.form.get('name'),
                "surname": request.form.get('surname')
            }
            db.edit_user(data)
            print(data)
        elif request.form.get("action") == "delete":
            db.delete_user(request.form.get("user_id"))
        users = db.get_info("users")
        return render_template("users.html", users=users)


if __name__ == '__main__':
    app.run()
