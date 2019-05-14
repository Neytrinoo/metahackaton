from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, DateField, TextAreaField, \
    MultipleFileField, RadioField, widgets, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, ValidationError, Length
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


class AddTask(FlaskForm):
    task_name = StringField('Название задачи', validators=[DataRequired()])
    description = TextAreaField('Описание задачи', validators=[DataRequired(), Length(1, 2000)])
    date_execution = DateField('Дата выполнения', format='%d.%m.%Y', validators=[Optional()])
    performer = StringField('Логин исполнителя', validators=[DataRequired()])
    priority = SelectField('Приоритет задачи',
                           choices=[(1, 'Совсем не срочная'), (2, 'Не срочная'), (3, 'Обычная'), (4, 'Срочная'),
                                    (5, 'Очень срочная')])
    execution_phase = SelectField('Этап выполнения',
                                  choices=[(1, 'Только начал'), (2, 'Кое-что готово'), (3, 'Много что сделал'),
                                           (4, 'Почти готова'), (5, 'Полностью выполнена')])
    category = StringField('Введите категорию задачи', validators=[Length(1, 100)])
    submit = SubmitField('Добавить задачу')

    def validate_performer(self, performer):
        user = User.query.filter_by(username=performer.data).first()
        if user is None:
            raise ValidationError('Такого пользователя нет в системе')
