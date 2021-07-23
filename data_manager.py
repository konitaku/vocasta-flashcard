import pandas as pd
# from pprint import pprint
from app import db
from flask_login import UserMixin
from datetime import datetime


class StudyLog(db.Model):
    __tablename__ = 'study_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'))
    num_of_learning = db.Column(db.Integer, default=1)
    num_of_remember = db.Column(db.Integer, default=0)
    initial_created_time = db.Column(db.DateTime, default=datetime.utcnow)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    word = db.relationship("Word")


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(300), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    study_logs = db.relationship("StudyLog", backref="user")


class Word(db.Model):
    __tablename__ = 'word'
    id = db.Column(db.Integer, primary_key=True)
    lang_name = db.Column(db.String(5), nullable=False)
    word = db.Column(db.String(50), nullable=False)
    japanese = db.Column(db.String(50), nullable=False)


def get_data(lang_name: str) -> list:
    df = pd.read_csv(f"{lang_name}.csv")
    print(f"Successfully Loaded Language: {lang_name}.")
    return df.to_dict(orient="records")


def get_data_from_db(lang_name: str) -> list:
    """Return Word List Retrieved From Database
    :rtype: object
    """
    data_list = db.session.query(Word).filter_by(lang_name=lang_name).all()
    if data_list:
        print(f"Successfully Loaded Language: {lang_name}")
        return [{f"{lang_name}": row.word, "ja": row.japanese, "word_id": row.id} for row in data_list]
    else:
        raise FileNotFoundError("NoneDataError")


# # -----データベースをリセットして作り直す時の記述-----
# db.drop_all()
db.create_all()


# # ------------CSVデータをデータベースに移行する記述---------------------
def append_word_data_to_db(lang_list: list):
    for lang in lang_list:
        word_list = get_data(lang)
        for word_dict in word_list:
            db_row = Word()
            db_row.lang_name = lang
            db_row.word = word_dict[lang]
            db_row.japanese = word_dict["ja"]
            db.session.add(db_row)
            db.session.commit()
        print(f"Successfully Added {lang} to the Database.")


# append_word_data_to_db(["en", "fr", "zh", "es", "ko"])
# ---------------------------------------------------------------

# ---------------- 学習記録をつけるときのサンプルコード -----------------
# https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#association-pattern
# user = User()
# user.name = "Takuma"
# user.email = "example@email.com"
# user.password = "password"
# db.session.add(user)
# db.session.commit()
#
# ユーザーオブジェクトのremembered_wordsプロパティに対象のWordオブジェクトをappend
# user.remembered_words.append(Word.query.get(10))
# db.session.commit()
# --------------------------------------------------------------
# ---------------- ユーザーの学習記録を取り出すサンプルコード --------------------
# user = User.query.get(1)
# for word in user.remembered_words:
#     if word.lang_name == "en":
#         print(word.lang_name)
#         print(word.word)
# >> en
# >> he
# --------------------------------------------------------------
