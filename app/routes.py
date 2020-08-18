from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse
from PIL import Image
import PIL
import os
from os.path import join, dirname, realpath
from werkzeug.utils import secure_filename
from app.models import User, Cat
import shutil
from time import sleep
from datetime import datetime
from helpers import *

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Front

@app.route("/")
def start():
    cats = Cat.query.all()
    return render_template("main.html", title="Fabryka Mruczenia", cats=cats)

@app.route("/cats/<string:val>")
def cats(val):

    if val == "kotki":
        cats = Cat.query.filter_by(sex="Kotka").filter_by(isActive=True).all()
        title = "Fabryka Mruczenia - Kotki"

    elif val == "koty":
        cats = Cat.query.filter_by(sex="Kot").filter_by(isActive=True).all()
        title = "Fabryka Mruczenia - Koty"

    elif val == "kociaki":
        cats = Cat.query.filter_by(isYoung=True).filter_by(isActive=True).all()
        title = "Fabryka Mruczenia - Kociaki"
    else:
        cats = Cat.query.filter_by(isActive=True).all()
        title = "Fabryka Mruczenia - Nasi podopieczni"

    cats_rows = [cats[i:i+4] for i in range(0, len(cats),4)]
    
    return render_template("cats.html", title=title, cats=cats_rows)

@app.route("/adopted/")
def adopted():
    
    cats = Cat.query.filter_by(isActive=False).all()
    title = "Fabryka Mruczenia - Wyadoptowani"

    cats_rows = [cats[i:i+4] for i in range(0, len(cats),4)]
    
    return render_template("adopted.html", title=title, cats=cats_rows)

@app.route("/cats/<string:name><int:id>")
def cat(name, id):
    found_cat = Cat.query.filter_by(id=id).filter_by(name=name).first()
    title = f"Fabryka Mruczenia - {name}"
    return render_template("cat.html", title=title, cat=found_cat)

@app.route("/ankieta/")
def ankieta():
    
    title = "Fabryka Mruczenia - Ankieta"
    return render_template("ankieta.html", title=title)

@app.route("/wizyta/")
def wizyta():
    
    title = "Fabryka Mruczenia - Wizyta Przedadopcyjna"
    return render_template("wizyta.html", title=title)

@app.route("/adopcja/")
def adopcja():
    
    title = "Fabryka Mruczenia - Adopcja"
    return render_template("adopcja.html", title=title)

@app.route("/pomoc/")
def pomoc(): 
    title = "Fabryka Mruczenia - Jak nam pomóc"
    return render_template("pomoc.html", title=title)

@app.route("/contact/")
def contact():
    title = "Fabryka Mruczenia - Kontakt"
    return render_template("contact.html", title=title)

@app.route("/codalej/")
def codalej():
    
    title = "Fabryka Mruczenia - Co dalej?"
    return render_template("codalej.html", title=title)

# Back

@app.route("/home/<string:val>")
@login_required
def homeFilter(val):
    if val == "active":
        val = True
        cats = Cat.query.filter_by(isActive=val).all()
    elif val == "notActive":
        val = False
        cats = Cat.query.filter_by(isActive=val).all()
    else:
        cats = Cat.query.all()

    if len(cats) == 0:
        noCats = True
    else:
        noCats = False

    howManyCats = len(cats)

    return render_template("home.html", title="Zarządzaj kotkami", cats=cats, noCats=noCats, howManyCats=howManyCats)

@app.route("/home/")
@login_required
def home():

    cats = Cat.query.filter_by(isActive=True).all()

    if len(cats) == 0:
        noCats = True
    else:
        noCats = False

    howManyCats = len(cats)
    
    return render_template("home.html", title="Zarządzaj kotkami", cats=cats, noCats=noCats, howManyCats=howManyCats)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/addCat/", methods=["GET", "POST"])
@login_required
def addCat():

    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        age = int(age)
        period = request.form["period"]
        sex = request.form["sex"]
        fur = request.form["fur"]
        when_came = request.form["when_came"]
        description = request.form["description"]
        currentlyOnMeds = request.form["currentlyOnMeds"]
        
        if currentlyOnMeds == "Tak":
            currentlyOnMeds = True
        else:
            currentlyOnMeds = False

        file = request.files["picture"]

        # if file and allowed_file(file.filename):
        #     filename = secure_filename(file.filename)
        #     file_path = os.path.join(join(dirname(realpath(__file__)), 'static/uploads/'), filename)
        #     file.save(file_path)
        if file and allowed_file(file.filename):
            file.filename = secure_filename(file.filename)
            output = str(upload_file_to_s3(file, "fabrykamruczenia"))

        googlePhoto1 = request.files["1photo"]
        if googlePhoto1 and allowed_file(googlePhoto1.filename):
            googlePhoto1.filename = secure_filename(googlePhoto1.filename)
            googlePhoto1URL = str(upload_file_to_s3(googlePhoto1, "fabrykamruczenia"))

        googlePhoto2 = request.files["2photo"]
        if googlePhoto2 and allowed_file(googlePhoto2.filename):
            googlePhoto2.filename = secure_filename(googlePhoto2.filename)
            googlePhoto2URL = str(upload_file_to_s3(googlePhoto2, "fabrykamruczenia"))
        
        googlePhoto3 = request.files["3photo"]
        if googlePhoto3 and allowed_file(googlePhoto3.filename):
            googlePhoto3.filename = secure_filename(googlePhoto3.filename)
            googlePhoto3URL = str(upload_file_to_s3(googlePhoto3, "fabrykamruczenia"))

        if (period == "Miesiąc" and age >= 3) or (period == "Rok"):
            isYoung = False
        else:
            isYoung = True
        
        if not isYoung and not currentlyOnMeds:
            readyToBeAdopted = True
        else:
            readyToBeAdopted = False

        cat = Cat(name=name, description=description, age=age, period=period, sex=sex, fur=fur, when_came=when_came, picture=output, isYoung=isYoung, readyToBeAdopted=readyToBeAdopted, currentlyOnMeds=currentlyOnMeds, googlePhoto1=googlePhoto1URL, googlePhoto2=googlePhoto2URL, googlePhoto3=googlePhoto3URL)
        db.session.add(cat)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("addCat.html", title="Dodaj kotka")

@app.route("/updateAges/", methods=["GET", "POST"])
@login_required
def updateAges():
   
    cats = Cat.query.all()

    for cat in cats:
        if cat.period == "Miesiąc":
            now = datetime.now()
            lastUpdate = cat.timestamp
            delta = now.month - lastUpdate.month
            delta = int(delta)
            cat.age += delta
            if cat.age >= 12:
                cat.period = "Rok"
                cat.age = (cat.age / 12)
            cat.timestamp = now

        elif cat.period == "Tydzień":
            now = datetime.now()
            lastUpdate = cat.timestamp
            delta = now.isocalendar()[1] - lastUpdate.isocalendar()[1]
            delta = int(delta)
            cat.age += delta
            if cat.age >= 8:
                cat.period = "Miesiąc"
                cat.age = int(cat.age / 4)
            cat.timestamp = now

        elif cat.period == "Rok":
            now = datetime.now()
            lastUpdate = cat.timestamp
            delta = now.year - lastUpdate.year
            delta = int(delta)
            cat.age += delta
            cat.timestamp = now
        
        if (cat.period == "Miesiąc" and cat.age >= 3) or (cat.period == "Rok"):
            isYoung = False
        else:
            isYoung = True

        if not cat.isYoung and not cat.currentlyOnMeds:
            readyToBeAdopted = True
        else:
            readyToBeAdopted = False

    
    db.session.commit()

    return redirect(url_for("home"))

@app.route("/update/<int:id>", methods=["POST", "GET", "UPDATE"])
@login_required
def updateCat(id):
    found_cat = Cat.query.filter_by(id=id).first()

    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        age = int(age)
        sex = request.form["sex"]
        period = request.form["period"]
        fur = request.form["fur"]
        when_came = request.form["when_came"]
        description = request.form["description"]
        currentlyOnMeds = request.form["currentlyOnMeds"]

        if currentlyOnMeds == "Tak":
            currentlyOnMeds = True
        else:
            currentlyOnMeds = False

        # file = request.files["picture"]

        # if file and allowed_file(file.filename):
        #     filename = secure_filename(file.filename)
        #     if filename != found_cat.picture:
        #         file_path = os.path.join(join(dirname(realpath(__file__)), 'static/uploads/'), found_cat.picture)
        #         os.remove(file_path)
        #         file_path = os.path.join(join(dirname(realpath(__file__)), 'static/uploads/'), filename)
        #         file.save(file_path)
        #         found_cat.picture = filename

        file = request.files["picture"]
        
        if file and allowed_file(file.filename):
            file.filename = secure_filename(file.filename)
            output = str(upload_file_to_s3(file, "fabrykamruczenia"))
            found_cat.picture = output

        googlePhoto1 = request.files["1photo"]
        if googlePhoto1 and allowed_file(googlePhoto1.filename):
            googlePhoto1.filename = secure_filename(googlePhoto1.filename)
            googlePhoto1URL = str(upload_file_to_s3(googlePhoto1, "fabrykamruczenia"))
            found_cat.googlePhoto1 = googlePhoto1URL

        googlePhoto2 = request.files["2photo"]
        if googlePhoto2 and allowed_file(googlePhoto2.filename):
            googlePhoto2.filename = secure_filename(googlePhoto2.filename)
            googlePhoto2URL = str(upload_file_to_s3(googlePhoto2, "fabrykamruczenia"))
            found_cat.googlePhoto2 = googlePhoto2URL
        
        googlePhoto3 = request.files["3photo"]
        if googlePhoto3 and allowed_file(googlePhoto3.filename):
            googlePhoto3.filename = secure_filename(googlePhoto3.filename)
            googlePhoto3URL = str(upload_file_to_s3(googlePhoto3, "fabrykamruczenia"))
            found_cat.googlePhoto3 = googlePhoto3URL


        if (period == "Miesiąc" and age >= 3) or (period == "Rok"):
            isYoung = False
        else:
            isYoung = True
        
        if not isYoung and not currentlyOnMeds:
            readyToBeAdopted = True
        else:
            readyToBeAdopted = False
        
        if period != found_cat.period:
            found_cat.period = period
        if name != found_cat.name:
            found_cat.name = name
        if age != found_cat.age:
            found_cat.age = age
        if sex != found_cat.sex:
            found_cat.sex = sex
        if fur != found_cat.fur:
            found_cat.fur = fur
        if when_came != found_cat.when_came:
            found_cat.when_came = when_came
        if description != found_cat.description:
            found_cat.description = description
        if isYoung != found_cat.isYoung:
            found_cat.isYoung = isYoung
        if readyToBeAdopted != found_cat.readyToBeAdopted:
            found_cat.readyToBeAdopted = readyToBeAdopted
        if currentlyOnMeds != found_cat.currentlyOnMeds:
            found_cat.currentlyOnMeds = currentlyOnMeds

        db.session.commit()
        
    return render_template("updateCat.html", title="Edytuj kotka", cat=found_cat)

@app.route("/adopt/<int:id>", methods=["POST", "GET", "UPDATE"])
@login_required
def adoptCat(id):

    found_cat = Cat.query.filter_by(id=id).first()

    if found_cat.isActive:
        found_cat.isActive = False
    else:
        found_cat.isActive = True

    db.session.commit()
    return redirect(url_for("home"))

@app.route("/delete/<int:id>", methods=["POST", "GET", "DELETE"])
@login_required
def deleteCat(id):
    found_cat = Cat.query.filter_by(id=id).first()

    file_path = os.path.join(join(dirname(realpath(__file__)), 'static/uploads/'), found_cat.picture)
    try:
        os.remove(file_path)
    except:
        pass

    db.session.delete(found_cat)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/login/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        return redirect("/home/")
    return render_template("login.html", title="Sign In", form=form)

@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for("login"))