# filepath: /home/patrick/larderlogic/create_admin.py
from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    username = input("Enter new admin username: ")
    password = input("Enter password: ")
    user = User(username=username, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    print("Admin user created.")