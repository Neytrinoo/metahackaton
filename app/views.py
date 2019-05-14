from app import app, db
from flask import render_template, flash, redirect, url_for, request
from werkzeug.security import generate_password_hash
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import *
from app.models import *
import pymorphy2

execution_phases = {1: 'Только начал',
                    2: 'Кое-что готово',
                    3: 'Много что сделал',
                    4: 'Почти готова',
                    5: 'Полностью выполнена'}
priotities = {1: 'Совсем не срочная',
              2: 'Не срочная',
              3: 'Обычная',
              4: 'Срочная',
              5: 'Очень срочная'}


@app.route('/')
def index():
    if not current_user.is_anonymous:
        tasks = current_user.author_tasks
        execution_phase = []
        priority = []
        todo_or_not_todo = []
        color_task = []
        for task in tasks:
            if (task.date_execution - datetime.now()).days < -1:
                color_task.append(False)
            else:
                color_task.append(True)
            execution_phase.append(execution_phases[task.execution_phase])
            priority.append(priotities[task.priority])
            if task.todo_or_not_todo is None:
                todo_or_not_todo.append('Не выполнена')
            else:
                todo_or_not_todo.append('Выполнена')
        return render_template('index.html', tasks=tasks, execution_phase=execution_phase, priority=priority,
                               todo_or_not_todo=todo_or_not_todo, color_task=color_task)
    else:
        return render_template('index.html')


@app.route('/delegated-tasks')
def delegated_tasks():
    if not current_user.is_anonymous:
        tasks = current_user.performer_tasks
        execution_phase = []
        priority = []
        todo_or_not_todo = []
        color_task = []
        for task in tasks:
            if (task.date_execution - datetime.now()).days < -1:
                color_task.append(False)
            else:
                color_task.append(True)
            execution_phase.append(execution_phases[task.execution_phase])
            priority.append(priotities[task.priority])
            if task.todo_or_not_todo is None:
                todo_or_not_todo.append('Не выполнена')
            else:
                todo_or_not_todo.append('Выполнена')
        return render_template('delegated_tasks.html', tasks=tasks, execution_phase=execution_phase, priority=priority,
                               todo_or_not_todo=todo_or_not_todo, color_task=color_task)
    else:
        return render_template('index.html')


@app.route('/last-task')
@login_required
def last_task():
    tasks = current_user.author_tasks
    execution_phase = []
    priority = []
    todo_or_not_todo = []
    color_task = []
    itogo_tasks = []
    for task in tasks:
        if (task.date_execution - datetime.now()).days >= -1:
            continue
        execution_phase.append(execution_phases[task.execution_phase])
        priority.append(priotities[task.priority])
        if task.todo_or_not_todo is None:
            todo_or_not_todo.append('Не выполнена')
        else:
            todo_or_not_todo.append('Выполнена')
        itogo_tasks.append(task)
    return render_template('last_task.html', tasks=itogo_tasks, execution_phase=execution_phase, priority=priority,
                           todo_or_not_todo=todo_or_not_todo, color_task=color_task)


@login_required
@app.route('/task/<int:id>')
def task_page(id):
    task = Task.query.filter_by(id=id).first()
    if task.author_id != current_user.id and task.performer_id != current_user.id:
        flash('Это не ваша задача')
        return redirect(url_for('index'))
    execution_phase = []
    priority = []
    todo_or_not_todo = []
    color_task = []
    if (task.date_execution - datetime.now()).days < -1:
        color_task = False
    else:
        color_task = True
    execution_phase = execution_phases[task.execution_phase]
    priority = priotities[task.priority]
    if task.todo_or_not_todo is None:
        todo_or_not_todo = 'Не выполнена'
    else:
        todo_or_not_todo = 'Выполнена'
    return render_template('tasks_page.html', task=task, execution_phase=execution_phase, priority=priority,
                           todo_or_not_todo=todo_or_not_todo, color_task=color_task)


@app.route('/delete-task/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_task(id):
    task = Task.query.filter_by(id=id).first()
    if task.author_id != current_user.id:
        flash('Это не ваша задача')
        return redirect(url_for('index'))
    Task.query.filter_by(id=id).delete()
    db.session.commit()
    flash('Задача успешно удалена')
    return redirect(url_for('index'))


@app.route('/edit-task/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    task = Task.query.filter_by(id=id).first()
    if task.author_id != current_user.id and task.performer_id != current_user.id:
        flash('Это не ваша задача')
        return redirect(url_for('index'))
    form = EditTaskForm()
    if form.validate_on_submit():
        task.name = form.task_name.data
        task.description = form.description.data
        task.date_execution = form.date_execution.data
        task.performer = User.query.filter_by(username=form.performer.data).first()
        task.priority = form.priority.data
        task.execution_phase = form.execution_phase.data
        task.category = form.category.data
        if form.status.data == '1':
            task.todo_or_not_todo = False
        else:
            task.todo_or_not_todo = True
        db.session.commit()
    form.task_name.data = task.name
    form.description.data = task.description
    form.date_execution.data = task.date_execution
    form.performer.data = task.performer.username
    form.priority.data = str(task.priority)
    form.execution_phase.data = str(task.execution_phase)
    form.category.data = task.category
    if task.todo_or_not_todo is None or not task.todo_or_not_todo:
        form.status.data = '1'
    else:
        form.status.data = '2'
    return render_template('edit_task.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user.check_password(form.password.data):
            flash('Неверное имя пользователя или пароль')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, name=form.name.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/add-task', methods=['GET', 'POST'])
@login_required
def add_task():
    form = AddTask()
    if form.validate_on_submit():
        task = Task(name=form.task_name.data, description=form.description.data,
                    date_execution=form.date_execution.data, category=form.category.data,
                    priority=int(form.priority.data),
                    execution_phase=int(form.execution_phase.data))
        current_user.author_tasks.append(task)
        db.session.add(task)
        db.session.commit()
        meta_tags = form.meta_tags.data.split(',')
        for i in range(len(meta_tags)):
            meta_tags[i] = meta_tags[i].lower().rstrip().lstrip()
            if len(meta_tags[i]) >= 600:
                continue
            if MetaTagsTask.query.filter_by(text=meta_tags[i]).first() is None:
                db.session.add(MetaTagsTask(text=meta_tags[i]))
            if MetaTagsTask.query.filter_by(text=meta_tags[i]).first() not in task.meta_tags:
                task.meta_tags.append(MetaTagsTask.query.filter_by(text=meta_tags[i]).first())
            db.session.commit()
        user = User.query.filter_by(username=form.performer.data).first()
        user.performer_tasks.append(task)
        db.session.commit()
        flash('Задача успешно добавлена')
        return redirect(url_for('index'))
    return render_template('add_task.html', form=form, title='Добавление задачи')


def task_delegate_search(search_text):
    morph = pymorphy2.MorphAnalyzer()
    search_text = search_text.split()
    need_tags = []
    task_tags = []
    for line in search_text:
        search_now = morph.parse(line.lower())[0].normal_form
        if MetaTagsTask.query.filter_by(text=search_now).first() is not None:
            need_tags.append(MetaTagsTask.query.filter_by(text=search_now).first())
    task_tags_count = {}
    for tag in need_tags:
        for task in tag.tasks:
            if task.performer_id == current_user.id:
                if task not in task_tags_count:
                    task_tags_count[task] = 1
                else:
                    task_tags_count[task] += 1
    task_tags_count = list(reversed(sorted(task_tags_count.items(), key=lambda x: x[1])))
    return ([x[0] for x in task_tags_count], need_tags)


def task_search(search_text):
    morph = pymorphy2.MorphAnalyzer()
    search_text = search_text.split()
    need_tags = []
    task_tags = []
    for line in search_text:
        search_now = morph.parse(line.lower())[0].normal_form
        if MetaTagsTask.query.filter_by(text=search_now).first() is not None:
            need_tags.append(MetaTagsTask.query.filter_by(text=search_now).first())
    task_tags_count = {}
    for tag in need_tags:
        for task in tag.tasks:
            if task.author_id == current_user.id:
                if task not in task_tags_count:
                    task_tags_count[task] = 1
                else:
                    task_tags_count[task] += 1
    task_tags_count = list(reversed(sorted(task_tags_count.items(), key=lambda x: x[1])))
    return ([x[0] for x in task_tags_count], need_tags)


# Функция поиска
@app.route('/search-author-tasks')
def search_author_tasks():
    search_text = request.args.get('search_input')
    copy_search_text = search_text
    if not search_text:
        flash('Поисковый запрос пуст')
        return redirect(url_for('index'))
    task_tags_count, need_tags = task_search(search_text)
    copy_search_text = search_text
    if not task_tags_count:
        flash('Ничего не найдено')
        return redirect(url_for('index'))
    views_name = []
    dates = []
    execution_phase = []
    priority = []
    todo_or_not_todo = []
    color_task = []
    for task in task_tags_count:
        if (task.date_execution - datetime.now()).days < -1:
            color_task.append(False)
        else:
            color_task.append(True)
        execution_phase.append(execution_phases[task.execution_phase])
        priority.append(priotities[task.priority])
        if task.todo_or_not_todo is None:
            todo_or_not_todo.append('Не выполнена')
        else:
            todo_or_not_todo.append('Выполнена')
    return render_template('index.html', tasks=task_tags_count, execution_phase=execution_phase, priority=priority,
                           todo_or_not_todo=todo_or_not_todo, color_task=color_task)

@app.route('/search-performer-tasks')
def search_performer_tasks():
    search_text = request.args.get('search_input')
    copy_search_text = search_text
    if not search_text:
        flash('Поисковый запрос пуст')
        return redirect(url_for('index'))
    task_tags_count, need_tags = task_delegate_search(search_text)
    copy_search_text = search_text
    if not task_tags_count:
        flash('Ничего не найдено')
        return redirect(url_for('index'))
    views_name = []
    dates = []
    execution_phase = []
    priority = []
    todo_or_not_todo = []
    color_task = []
    for task in task_tags_count:
        if (task.date_execution - datetime.now()).days < -1:
            color_task.append(False)
        else:
            color_task.append(True)
        execution_phase.append(execution_phases[task.execution_phase])
        priority.append(priotities[task.priority])
        if task.todo_or_not_todo is None:
            todo_or_not_todo.append('Не выполнена')
        else:
            todo_or_not_todo.append('Выполнена')
    return render_template('index.html', tasks=task_tags_count, execution_phase=execution_phase, priority=priority,
                           todo_or_not_todo=todo_or_not_todo, color_task=color_task)

@app.route('/logout')
@login_required
def logout():
    logout_user()  # Разлогиниваем пользователя
    return redirect(url_for('index'))
