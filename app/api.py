from flask import jsonify
from flask_restful import Resource, abort, reqparse

api = Api(app)

marks = ["1", "2", "3", "4", "5"]

auth_parser = reqparse.RequestParser()
auth_parser.add_argument("username", required=True)
auth_parser.add_argument("password", required=True)


class AuthResource(Resource):

    @staticmethod
    def post():
        args = auth_parser.parse_args()
        username = args.get["username"]
        password = args.get["password"]
        user = User.query.filter_by(username=username).first()
        if not user:
            abort(404, message="No such User")
        if user.check_password(password):
            return jsonify({"token": user.token})
        else:
            return abort(403, message="Wrong password")


task_parser = reqparse.RequestParser()
task_parser.add_argument("token", required=True)

put_task_parser = reqparse.RequestParser()
put_task_parser.add_argument("token", required=True)
put_task_parser.add_argument("name")
put_task_parser.add_argument("category")
put_task_parser.add_argument("description")
put_task_parser.add_argument("date_execution")
put_task_parser.add_argument("author_id")
put_task_parser.add_argument("performer_id")
put_task_parser.add_argument("priority")
put_task_parser.add_argument("execution_phase")
put_task_parser.add_argument("todo_or_not_todo")

post_task_parser = reqparse.RequestParser()
post_task_parser.add_argument("token", required=True)
post_task_parser.add_argument("name")
post_task_parser.add_argument("category")
post_task_parser.add_argument("description")
post_task_parser.add_argument("date_execution")


class TaskResource(Resource):

    @staticmethod
    def get(task_id=None):
        args = task_parser.parse_args()
        user = User.query.filter_by(token=args["token"]).first()
        if not user:
            abort(404, message="User not found")
        if not task_id:
            tasks = Task.query.filter_by(author_id=user.id).all()
            return jsonify({"tasks": [{"id": task.id,
                                       "name": task.name,
                                       "category": task.category,
                                       "description": task.description,
                                       "date_execution": task.date_execution,
                                       "author_id": task.author_id,
                                       "performer_id": task.performer_id,
                                       "priority": task.priority,
                                       "execution_phase": task.execution_phase,
                                       "todo_or_not_todo": task.todo_or_not_todo
                                       } for task in tasks]})
        else:
            task = Task.query.filter_by(id=task_id).first()
            if not task:
                abort(404, message="Not found")
            return jsonify({"task": {
                "id": task.id,
                "name": task.name,
                "category": task.category,
                "description": task.description,
                "date_execution": task.date_execution,
                "author_id": task.author_id,
                "performer_id": task.performer_id,
                "priority": task.priority,
                "execution_phase": task.execution_phase,
                "todo_or_not_todo": task.todo_or_not_todo
            }})

    @staticmethod
    def put(task_id):
        args = put_task_parser.parse_args()
        user = User.query.filter_by(token=args["token"]).first()
        if not user:
            abort(404, message="User not found")
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            abort(404, message="Not found task")
        try:
            task.name = args.get("name", task.name)
            task.category = args.get("category", task.category)
            task.description = args.get("description", task.description)
            task.date_execution = args.get("date_execution", task.date_execution)
            task.author_id = args.get("author_id", task.author_id)
            task.performer_id = args.get("performer_id", task.performer_id)
            task.priority = args.get("priority", task.priority) if args.get("priority", task.priority) in marks else "0"
            task.execution_phase = args.get("execution_phase", task.execution_phase)
            task.todo_or_not_todo = args.get("todo_or_not_todo", task.todo_or_not_todo)
            db.session.commit()
            return "OK!"
        except Exception:
            abort(400, message="Wrong data")

    @staticmethod
    def delete(task_id):
        args = put_task_parser.parse_args()
        user = User.query.filter_by(token=args["token"]).first()
        if not user:
            abort(404, message="User not found")
        Task.query.filter_by(id=task_id).delete()
        db.session.commit()

    @staticmethod
    def post():
        args = post_task_parser.parse_args()
        user = User.query.filter_by(api_key=args["token"]).first()
        if not user:
            abort(403, message="Wrong User")
        try:
            task = Task(name=args["name"],
                        description=args["description"],
                        date_execution=args["date_execution"],
                        author_id=user.id,
                        performer_id=user.id,
                        category=args.get("category", ""),
                        priority="0",
                        execution_phase="0",
                        todo_or_not_todo=False)
            db.session.add(task)
            db.session.commit()
            return "OK!"
        except Exception:
            abort(400, message="Wrong data")


api.add_resource(TaskResource, '/api/task')
api.add_resource(TaskResource, '/api/task/<int:id>')
api.add_resource(AuthResource, '/api/auth')
