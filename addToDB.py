from app import db
from app.models import User, Cat

u = User(username="fabrykaAdmin")
u.set_password("kitku987")
db.session.add(u)
db.session.commit()