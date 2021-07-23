from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField
from wtforms.validators import DataRequired, Email


class RegisterForm(FlaskForm):
    name = StringField(label="ユーザーネーム", validators=[DataRequired(message="ユーザーネームを入力してください")])
    email = StringField(label="メールアドレス", validators=[DataRequired(message="メールアドレスを入力してください"), Email()])
    password = PasswordField(label="パスワード", validators=[DataRequired(message="パスワードを入力してください")])
    submit = SubmitField(label="登録")


class LoginForm(FlaskForm):
    email = StringField(label="メールアドレス", validators=[DataRequired(message="メールアドレスを入力してください"), Email()])
    password = PasswordField(label="パスワード", validators=[DataRequired(message="パスワードを入力してください")])
    submit = SubmitField(label="ログイン")


class EditWordForm(FlaskForm):
    word = StringField(label="単語", validators=[DataRequired(message="変更する単語を入力してください")])
    ja = StringField(label="和訳", validators=[DataRequired(message="変更する和訳を入力してください")])
    submit = SubmitField(label="変更")
