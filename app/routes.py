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

# Route: Landing page
@app.route("/")
def start():
    cats = Cat.query.all()
    return render_template("main.html", title="Fabryka Mruczenia", cats=cats)


# Route: Lista kotów
@app.route("/cats/<string:val>")
def cats(val):

    if val == "kotki":
        cats = Cat.query.filter_by(sex="Kotka").filter_by(isActive=True).all()
        title = "Kotki | Fabryka Mruczenia"

    elif val == "koty":
        cats = Cat.query.filter_by(sex="Kot").filter_by(isActive=True).all()
        title = "Koty | Fabryka Mruczenia"

    elif val == "kociaki":
        cats = Cat.query.filter_by(isYoung=True).filter_by(isActive=True).all()
        title = "Kociaki | Fabryka Mruczenia"
    else:
        cats = Cat.query.filter_by(isActive=True).all()
        title = "Nasi podopieczni | Fabryka Mruczenia"

    cats_rows = [cats[i:i+4] for i in range(0, len(cats),4)]
    
    return render_template("cats.html", title=title, cats=cats_rows)


# Route: Lista wyadoptowanych
@app.route("/adopted/")
def adopted():
    
    cats = Cat.query.filter_by(isActive=False).all()
    title = "Wyadoptowani | Fabryka Mruczenia"

    cats_rows = [cats[i:i+4] for i in range(0, len(cats),4)]
    
    return render_template("adopted.html", title=title, cats=cats_rows)


# Route: Strona kota
@app.route("/cats/<string:name>/<int:id>")
def cat(name, id):
    found_cat = Cat.query.get(id)
    title = f"{name} | Fabryka Mruczenia"
    return render_template("cat.html", title=title, cat=found_cat)


# Route: Static content
@app.route("/<string:static>/")
def content(static):

    txt = static

    try:
        x = static.split("-")
        txt = f"{x[0]} {x[1]}"
    except:
        pass

    title = f"{txt} | Fabryka Mruczenia"
    return render_template(f"{static}.html", title=title)



# BACK-END

# Dopuszczone rozszeszenia plików

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Funkcja: Adopcja kota
@app.route("/adopt/<int:id>", methods=["POST", "GET", "UPDATE"])
@login_required
def adoptCat(id):

    found_cat = Cat.query.get(id)

    if found_cat.isActive:
        found_cat.isActive = False
    else:
        found_cat.isActive = True

    db.session.commit()
    return redirect(url_for("home"))


# Funkcja: Update'u wieku kotów
@app.route("/updateAges/", methods=["GET", "POST"])
@login_required
def updateAges():
   
    cats = Cat.query.all()

    now = datetime.now()

    for cat in cats:
        if cat.period == "Tydzień":
            lastUpdate = cat.timestamp
            delta = now.isocalendar()[1] - lastUpdate.isocalendar()[1]
            delta = int(delta)
            cat.age += delta
            if cat.age >= 8:
                cat.period = "Miesiąc"
                cat.age = int(cat.age / 4)

        elif cat.period == "Miesiąc":
            lastUpdate = cat.timestamp
            delta = now.month - lastUpdate.month
            delta = int(delta)
            cat.age += delta
            if cat.age >= 12:
                cat.period = "Rok"
                cat.age = int(cat.age / 12)
            lastUpdate = cat.timestamp            

        elif cat.period == "Rok":
            lastUpdate = cat.timestamp
            delta = now.year - lastUpdate.year
            delta = int(delta)
            cat.age += delta
        
        if (cat.period == "Miesiąc" and cat.age >= 3) or (cat.period == "Rok"):
            isYoung = False
        else:
            isYoung = True

        if not cat.isYoung and not cat.currentlyOnMeds:
            readyToBeAdopted = True
        else:
            readyToBeAdopted = False
        
        cat.timestamp = now

    
    db.session.commit()

    return redirect(url_for("home"))


# Funkcja: Usunięcie kota
@app.route("/delete/<int:id>", methods=["POST", "GET", "DELETE"])
@login_required
def deleteCat(id):
    found_cat = Cat.query.get(id)

    photos = [found_cat.picture.split("/")[-1], found_cat.googlePhoto1.split("/")[-1], found_cat.googlePhoto2.split("/")[-1], found_cat.googlePhoto3.split("/")[-1]]
    
    for photo in photos:
        delete_file_from_s3(photo)
    
    db.session.delete(found_cat)
    db.session.commit()
    return redirect(url_for("home"))


# Route: Lista kotów z filtrami
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


# Route: Lista kotów ogólna default
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


# Route: Dodawanie kotów
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

        if file and allowed_file(file.filename):
            file.filename = secure_filename(file.filename)
            output = str(upload_file_to_s3(file, "fabrykamruczenia"))

        googlePhotos = []

        for i in range(1, 4):
            googlePhoto = request.files[f"{i}photo"]
            if googlePhoto and allowed_file(googlePhoto.filename):
                googlePhoto.filename = secure_filename(googlePhoto.filename)
                googlePhotoURL = str(upload_file_to_s3(googlePhoto, "fabrykamruczenia"))
                googlePhotos.append(googlePhotoURL)

        if (period == "Miesiąc" and age >= 3) or (period == "Rok"):
            isYoung = False
        else:
            isYoung = True
        
        if not isYoung and not currentlyOnMeds:
            readyToBeAdopted = True
        else:
            readyToBeAdopted = False

        cat = Cat(name=name, description=description, age=age, period=period, sex=sex, fur=fur, when_came=when_came, picture=output, isYoung=isYoung, readyToBeAdopted=readyToBeAdopted, currentlyOnMeds=currentlyOnMeds, googlePhoto1=googlePhotos[0], googlePhoto2=googlePhotos[1], googlePhoto3=googlePhotos[2])
        db.session.add(cat)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("addCat.html", title="Dodaj kotka")


# Route: Edycja kota
@app.route("/update/<int:id>", methods=["POST", "GET"])
@login_required
def updateCat(id):
    found_cat = Cat.query.filter_by(id=id).first()
    backup = found_cat

    if request.method == "POST":

        props = {
            "name": request.form["name"],
            "age": int(request.form["age"]),
            "period": request.form["period"],
            "sex": request.form["sex"], 
            "fur": request.form["fur"],
            "when_came": request.form["when_came"],
            "description": request.form["description"],
            "currentlyOnMeds": request.form["currentlyOnMeds"],            
            }

        if props["currentlyOnMeds"] == "Tak":
            props["currentlyOnMeds"] = True
        else:
            props["currentlyOnMeds"] = False

        file = request.files["picture"]
        
        if file and allowed_file(file.filename):

            photo = found_cat.picture.split("/")[-1]
            delete_file_from_s3(photo)

            file.filename = secure_filename(file.filename)
            output = str(upload_file_to_s3(file, "fabrykamruczenia"))
            found_cat.picture = output

        googlePhotos = [found_cat.googlePhoto1, found_cat.googlePhoto1, found_cat.googlePhoto1]

        for i in range(1, 4):
            googlePhoto = request.files[f"{i}photo"]
            if googlePhoto and allowed_file(googlePhoto.filename):

                photo = googlePhotos[i - 1].split("/")[-1]
                delete_file_from_s3(photo)

                googlePhoto.filename = secure_filename(googlePhoto.filename)
                googlePhotoURL = str(upload_file_to_s3(googlePhoto, "fabrykamruczenia"))
                setattr(found_cat, f"googlePhoto{i}", googlePhotoURL)


        if (props["period"] == "Miesiąc" and props["age"] >= 3) or (props["period"] == "Rok"):
            props["isYoung"] = False
        else:
            props["isYoung"] = True
        
        if not props["isYoung"] and not props["currentlyOnMeds"]:
            props["readyToBeAdopted"] = True
        else:
            props["readyToBeAdopted"] = False
                
        for attr, value in props.items():
            if value != getattr(found_cat, attr):
                setattr(found_cat, attr, value)

        db.session.commit()

        return redirect(url_for("home"))

    return render_template("updateCat.html", title="Edytuj kotka", cat=found_cat)


# Route: Login
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


# Funkcja: Logout
@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for("login"))