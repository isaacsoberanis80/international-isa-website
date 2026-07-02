from .models import db, Lead, User, Task


def save_lead(name, email, phone, brokerage, message):
    lead = Lead(name=name, email=email, phone=phone, brokerage=brokerage, message=message)
    db.session.add(lead)
    db.session.commit()


def get_all_leads():
    return Lead.query.order_by(Lead.created_at.desc()).all()


def update_lead_status(lead_id, status):
    lead = db.session.get(Lead, lead_id)
    if lead:
        lead.status = status
        db.session.commit()


def create_user(username, password_hash):
    user = User(username=username, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()


def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


def get_user_by_id(user_id):
    return db.session.get(User, int(user_id))


def add_task(user_id, description):
    task = Task(user_id=user_id, description=description)
    db.session.add(task)
    db.session.commit()


def get_tasks_for_user(user_id):
    return Task.query.filter_by(user_id=user_id).order_by(Task.done.asc(), Task.created_at.desc()).all()


def complete_task(task_id, user_id):
    task = db.session.get(Task, task_id)
    if task and task.user_id == user_id:
        task.done = True
        db.session.commit()
