from flask import Flask, render_template, flash, redirect, session, request, abort, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///beveragebot.sqlite3'

db = SQLAlchemy(app)


class drinkList(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    code = db.Column(db.UnicodeText)
    desc = db.Column(db.String(200))
    numPours = db.Column(db.Integer, default=0)
    fav = db.Column(db.Boolean, default=False)

    def __init__(self, name, code, desc):
        self.name = name
        self.code = code
        self.desc = desc

# def __init__(self, name, city, addr,pin):
#   self.name = name
#   self.city = city
#   self.addr = addr
#   self.pin = pin


class pourLog(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    code = db.Column(db.UnicodeText)
    pourSize = db.Column(db.Integer)
    batchNum = db.Column(db.Integer)


class tapList(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    # refers to physical tap, if unavailable do -1
    source = db.Column(db.String(100), unique=True)
    # refers to code name identifier
    name = db.Column(db.String(100), unique=True)
    display = db.Column(db.String(100), unique=True)  # refers to display name
    refillDate = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    capacity = db.Column(db.Integer)  # quantity in mL
    poured = db.Column(db.Integer)  # quantity in mL
    # can this drink be poured (false if out or if not on tap)
    available = db.Column(db.Boolean)

    def __init__(self, source, name, display, capacity, poured, available):
        self.source = source
        self.name = name
        self.display = display
        self.capacity = capacity
        self.poured = poured
        self.available = available


@app.route("/")
def main():
    return render_template('home.html')


@app.route("/drinks")
def drinks():
    #test = drinkList("Coke with Lime", "h20: 0.7, coke: 0.25, lime: 0.05", "Just Coca Cola")
    #db.session.add(test)
    #db.session.commit()
    drinks = db.session.query(drinkList).all()
    return render_template('drinks.html', drinks=drinks)

@app.route("/drinks/create", methods = ['POST', 'GET'])
def drinksCreate():
    if request.method == 'POST':
        result = request.form
        fail = False
        msg = ""
        portionTotal = 0
        if len(result["dname"]) == 0 or len(result["dname"]) > 100:
            fail = True
            msg = "Incorrect name"
        if len(result["ddesc"]) == 0 or len(result["ddesc"]) > 200:
            fail = True
            msg = "Incorrect description"
        for j, k in result.items():
            j = j.split("-", 1)
            if j[0] == "portion":
                portionTotal = portionTotal + float(k)
                if int(k) < 0:
                    fail = True
                    msg = "Incorrect portioning"
        if fail:
            taps = db.session.query(tapList).all()
            return render_template('drinks.create.html', taps=taps, result = result, fail = True, msg = msg)
        else:
            drinkCode = []
            for j, k in result.items():
                j = j.split("-", 1)
                if j[0] == "portion":
                    drinkCode.append(j[1] + ": " + str(float(k)/portionTotal))
            newDrink = drinkList(result["dname"], ", ".join(drinkCode), result["ddesc"])
            db.session.add(newDrink)
            db.session.commit()
            #taps = db.session.query(tapList).all()
            #return render_template('drinks.create.html', taps=taps, result = result)
            return redirect(url_for('drinks'), success = result['dname'])
    else:
        taps = db.session.query(tapList).all()
        return render_template('drinks.create.html', taps=taps, result = {})




@app.route("/taplist")
def taplist():
    # Creation Example
    #test = tapList("tap4", "van", "Vanilla Syrup", "200", "0", True)
    #db.session.add(test)
    #db.session.commit()
    taps = db.session.query(tapList).all()
    return render_template('taplist.html', taps=taps)


@app.route("/manage")
def manage():

    return render_template('manage.html')

# Example left in case weird url names will be needed


@app.route("/hello/<string:name>/")
def hello(name):
    return render_template(
        './test.html', name=name)


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
