import os
from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_sqlalchemy import SQLAlchemy
from forms import RegisterForm, LoginForm, EditWordForm
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
Bootstrap(app)
login_manager = LoginManager(app)
DIFF_JST_FROM_UTC = 9
QUIZ_LENGTH = 10
LANG_LIST = ["en", "fr", "zh", "es", "ko"]
LANG_HEADINGS = {"en": "英語", "fr": "フランス語", "zh": "中国語", "es": "スペイン語", "ko": "韓国語"}


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


def date_duration_calc(date: datetime) -> int:
    try:
        duration = (datetime.utcnow() - date).days
        today_str = (datetime.utcnow() + timedelta(hours=DIFF_JST_FROM_UTC)).strftime("%Y%m/%d")
        date_str = (date + timedelta(hours=DIFF_JST_FROM_UTC)).strftime("%Y%m/%d")

        # 年と月が一緒なら日付の差をdurationに代入
        if today_str.split("/")[0] == date_str.split("/")[0]:
            duration = int(today_str.split("/")[1]) - int(date_str.split("/")[1])

    except AttributeError:
        duration = None
    except TypeError:
        duration = None
    return duration


def extract_max_datetime(logs: list) -> datetime:
    new_list = [item.updated_time for item in logs]
    try:
        max_date = max(new_list)
    except ValueError:
        max_date = None
    return max_date


def duration_int_to_date(days: int) -> str:
    try:
        heading = "前回学習日: "
        if days == 0:
            date = "今日"
        elif days <= 5:
            date = f"{days}日前"
        else:
            date = datetime.utcnow() - timedelta(days=days) + timedelta(hours=DIFF_JST_FROM_UTC)
            date = date.strftime("%Y年%m月%d日")

        date = heading + date
    except TypeError:
        date = ""
    return date


@login_manager.user_loader
def load_user(user_id):
    from data_manager import User
    user = User.query.get(user_id)
    print(user.name)
    return user


@app.route("/")
def home():
    from data_manager import StudyLog
    # print(StudyLog.query.filter_by(user_id=1).all())
    user_scores = []

    for _ in LANG_LIST:
        user_scores.append(0)

    if current_user.is_authenticated:
        user_score = len([item for item in current_user.study_logs if item.num_of_remember != 0])

        index = 0
        for lang in LANG_LIST:
            user_scores[index] = len([item for item in current_user.study_logs if item.word.lang_name == lang and
                                      item.num_of_remember != 0])
            index += 1
        print(user_scores)

        return render_template("index.html", user_score=user_score, user_scores=user_scores,
                               lang_list=LANG_LIST, lang_headings=LANG_HEADINGS, date_duration_calc=date_duration_calc,
                               StudyLog=StudyLog, extract_max_datetime=extract_max_datetime,
                               duration_int_to_date=duration_int_to_date,
                               page_name="ホーム")
    else:
        return render_template("lp.html", page_name="「ことば」をもっと身近に。")


@app.route("/inspect/<lang>/<index>")
def inspect_words(lang: str, index: str):
    # get_data_from_dbをインポート
    from data_manager import get_data_from_db

    # リンクの第一引数がおかしかったらホームにリダイレクト
    if not (lang in LANG_LIST):
        return redirect(url_for("home"))

    # 単語の全データを取得
    word_list = get_data_from_db(lang)

    # 問題数の分だけキリトリ
    word_from = int(index.split("-")[0])
    word_to = int(index.split("-")[1])

    # リンクの第二引数がおかしかったらホームにリダイレクト
    if word_to < word_from or word_from < 0 or word_to < 0 or word_from > 3000 or word_to > 3000:
        return redirect(url_for("home"))

    word_list = word_list[word_from - 1:word_to]
    return render_template("inspect-words.html", word_list=word_list, lang=lang, page_name="点検")


@app.route("/quiz/<lang>/<index>")
def quiz(lang: str, index: str):
    # get_data_from_dbをインポート
    from data_manager import get_data_from_db, append_word_data_to_db

    # リンクの第一引数がおかしかったらホームにリダイレクト
    if not (lang in LANG_LIST):
        return redirect(url_for("home"))

    # 単語の全データを取得
    try:
        word_list = get_data_from_db(lang)
    except FileNotFoundError:
        append_word_data_to_db(LANG_LIST)
        word_list = get_data_from_db(lang)

    # 問題数の分だけキリトリ
    word_from = int(index.split("-")[0])
    word_to = int(index.split("-")[1])

    # リンクの第二引数がおかしかったらホームにリダイレクト
    if word_to < word_from or word_from < 0 or word_to < 0 or word_from > 3000 or word_to > 3000:
        return redirect(url_for("home"))

    word_list = word_list[word_from-1:word_to]
    return render_template("word-quiz.html", lang=lang, index=index, word_list=word_list, page_name="単語クイズ")


@app.route("/result", methods=["GET", "POST"])
def result():
    if request.method == "POST":
        from data_manager import Word, StudyLog, get_data_from_db
        # フォームからクイズの結果リストなどを取得
        correct_ans = eval(request.form["result"])
        word_list = eval(request.form["word-list"])
        lang = request.form["lang-name"]

        print(correct_ans)
        print(word_list)

        word_id_list = [word.get("word_id") for word in word_list]

        new_word_list = get_data_from_db(lang)
        reloaded_word_list = []
        for word in new_word_list:
            if word["word_id"] in word_id_list:
                reloaded_word_list.append(word)

        correct_ans_id_list = [word.get("word_id") for word in correct_ans]
        correct_words = [word.get(lang) for word in correct_ans]

        next_word_from = max(word_id_list) + 1
        next_word_to = max(word_id_list) + QUIZ_LENGTH
        new_index = str(next_word_from) + "-" + str(next_word_to)

        if current_user.is_authenticated:
            for word_id in word_id_list:
                word_data = Word.query.get(word_id)
                past_log = [log_obj for log_obj in current_user.study_logs if log_obj.word_id == word_data.id]

                try:
                    print(past_log)
                    print(past_log[0])
                    past_log = db.session.query(StudyLog).get(past_log[0].id)
                    print(past_log.num_of_learning)
                    past_log.num_of_learning += 1

                    if word_id in correct_ans_id_list:
                        past_log.num_of_remember += 1

                    print(past_log.num_of_learning)
                    print(past_log.num_of_remember)
                    db.session.commit()
                    print(f"StudyLog is updated :{word_id} at {datetime.utcnow()}")

                except IndexError:
                    study_log = StudyLog(user_id=current_user.id, word_id=word_data.id)
                    if word_id in correct_ans_id_list:
                        study_log.num_of_remember = 1
                    db.session.add(study_log)
                    db.session.commit()
                    print(f"StudyLog is created :{word_id} at {datetime.utcnow()}")

        return render_template("result.html",
                               correct_words=correct_words,
                               word_list=reloaded_word_list,
                               lang=lang,
                               new_index=new_index,
                               page_name="結果")
    
    return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        from data_manager import User
        name = form.name.data
        email = form.email.data
        password = form.password.data
        if not db.session.query(User).filter_by(email=email).first():
            if len(password) >= 12:
                new_user = User()
                new_user.name = name
                new_user.email = email
                new_user.password = generate_password_hash(password)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                flash(f"ようこそ、{name}さん", "success")
                return redirect(url_for("home"))
            else:
                flash("パスワードは12文字以上にしてください")
    return render_template("register.html", form=form, page_name="アカウント作成")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        from data_manager import User
        email = form.email.data
        password = form.password.data
        user = db.session.query(User).filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash(f"おかえりなさい、{user.name}さん", "success")
                login_user(user)
                return redirect(url_for("home"))
            else:
                flash("パスワードが間違っています", "error")
        else:
            flash("メールアドレスが間違っている、もしくはユーザー未登録です", "error")

    return render_template("login.html", form=form, page_name="Vocastaにログイン")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/edit-word/<word_id>", methods=["GET", "POST"])
@admin_only
def edit_word(word_id: str):
    from data_manager import Word
    editing_word = Word.query.get(word_id)

    past_word = editing_word.word
    past_ja = editing_word.japanese

    form = EditWordForm(
        word=editing_word.word,
        ja=editing_word.japanese
    )
    if form.validate_on_submit():
        edited_word = db.session.query(Word).get(word_id)

        new_word = form.word.data
        new_ja = form.ja.data

        edited_word.word = new_word
        edited_word.japanese = new_ja

        db.session.commit()
        flash(f'Successfully Changed Word Properties', "success")
        flash(f'"{past_word}" to "{new_word}"', "success")
        flash(f'"{past_ja}" to "{new_ja}"', "success")
        return redirect(url_for("home"))

    return render_template("edit-word.html", word=editing_word, form=form, page_name="単語データ編集")


@app.route("/about")
def about():
    return render_template("getting-ready.html", page_name="Vocastaについて")


@app.route("/how-to-use")
def howto_use():
    return render_template("getting-ready.html", page_name="使い方")


if __name__ == "__main__":
    app.run(debug=True)
