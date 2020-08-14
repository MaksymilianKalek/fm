from app import db
from app.models import User, Cat

u = User(username="kur")
u.set_password("kur")
db.session.add(u)
db.session.commit()