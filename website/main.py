from flask import Flask, render_template, flash, redirect, session, request, abort
from flask_sqlalchemy import SQLAlchemy
import datetime
app = Flask(__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///beveragebot.sqlite3'

db = SQLAlchemy(app)

class drinkList(db.Model):
   id = db.Column('id', db.Integer, primary_key = True)
   name = db.Column(db.String(100), unique=True)
   code = db.Column(db.UnicodeText)
   desc = db.Column(db.String(200))
   numPours = db.Column(db.Integer)
   fav = db.Column(db.Boolean)

#def __init__(self, name, city, addr,pin):
#   self.name = name
#   self.city = city
#   self.addr = addr
#   self.pin = pin

class pourLog(db.Model):
   id = db.Column('id', db.Integer, primary_key = True)
   time = db.Column(db.DateTime)
   code = db.Column(db.UnicodeText)
   pourSize = db.Column(db.Integer)
   batchNum = db.Column(db.Integer)

class tapList(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    source = db.Column(db.String(100), unique=True) # refers to physical tap, if unavailable do -1
    name = db.Column(db.String(100), unique=True) # refers to code name identifier
    display = db.Column(db.String(100), unique=True) # refers to display name
    refillDate = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    capacity = db.Column(db.Integer) # quantity in mL
    poured = db.Column(db.Integer) # quantity in mL
    available = db.Column(db.Boolean) # can this drink be poured (false if out or if not on tap)

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
    return render_template('drinks.html')

@app.route("/taplist")
def taplist():
    #test = tapList("", "ging", "Ginger Syrup", "200", "0", False)
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
    './test.html',name=name)

if __name__ == "__main__":
    db.create_all()
    app.run(debug = True)

