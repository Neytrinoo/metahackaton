from app import app, db
from app.models import CategoryTask, Task
cat = CategoryTask(text='программирование')
db.session.add(cat)
db.session.commit()