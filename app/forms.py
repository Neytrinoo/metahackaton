from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, DateField, TextAreaField, \
    MultipleFileField, RadioField, widgets
from wtforms.validators import DataRequired, Email, EqualTo, Optional, ValidationError
from app.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    name = StringField('Имя, Фамилия', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    repeat_password = PasswordField('Повторите пароль', validators=[EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Такой пользователь уже зарегистрирован')
        if len(username.data) >= 100:
            raise ValidationError('Длина не должна превышать 100 символов')

    def validate_name(self, username):
        if len(username.data) >= 100:
            raise ValidationError('Длина не должна превышать 100 символов')

    def validate_password(self, password):
        if len(password.data) >= 120:
            raise ValidationError('Длина не должна превышать 120 символов')


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is None:
            raise ValidationError('Такого пользователя нет в системе')
