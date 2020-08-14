from app import db
from app.models import User, Cat
import sys

u = User(username=str(sys.argv[0]))
u.set_password(str(sys.argv[1]))
db.session.add(u)
db.session.commit()