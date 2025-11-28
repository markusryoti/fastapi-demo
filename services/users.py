from datetime import datetime, timedelta

from models.user import User

fake_users_db = {
    "johndoe@example.com": {
        "id": "257594e1-47ec-4e12-9f2d-83daa8912b23",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "password": "$argon2id$v=19$m=65536,t=3,p=4$wagCPXjifgvUFBzq4hqe3w$CYaIb8sB+wtD+Vu/P4uod1+Qof8h+1g7bbDlBID48Rc",
        "created_at": datetime.now() - timedelta(days=30),
    },
    "alice@example.com": {
        "id": 2,
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "password": "$argon2id$v=19$m=65536,t=3,p=4$wagCPXjifgvUFBzq4hqe3w$CYaIb8sB+wtD+Vu/P4uod1+Qof8h+1g7bbDlBID48Rc",
        "created_at": datetime.now() - timedelta(days=60),
    },
    "bob@example.com": {
        "id": 3,
        "full_name": "Bob Smith",
        "email": "bob@example.com",
        "password": "$argon2id$v=19$m=65536,t=3,p=4$wagCPXjifgvUFBzq4hqe3w$CYaIb8sB+wtD+Vu/P4uod1+Qof8h+1g7bbDlBID48Rc",
        "created_at": datetime.now() - timedelta(days=90),
    },
}


def get_users():
    return list(fake_users_db.values())


def get_user(email: str):
    if email in fake_users_db:
        user_dict = fake_users_db[email]
        return User(**user_dict)
