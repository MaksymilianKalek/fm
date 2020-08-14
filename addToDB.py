from app import db
from app.models import User, Cat

u = User(username="admin")
u.set_password("admin")
db.session.add(u)
db.session.commit()