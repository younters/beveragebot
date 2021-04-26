from flask import Flask, render_template, flash, redirect, session, request, abort, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_serial import Serial
from flask_socketio import SocketIO, send, emit
import datetime, json, time

import eventlet
#eventlet.monkey_patch()


app = Flask(__name__)
app.secret_key = b'_5#y2L"FIkldHUFU4Q8POK$z\n\xec]/'
app.config['SERIAL_TIMEOUT'] = 1
app.config['SERIAL_PORT'] = '/dev/cu.usbmodem14101'
app.config['SERIAL_BAUDRATE'] = 115200
app.config['SERIAL_BYTESIZE'] = 8
app.config['SERIAL_PARITY'] = 'N'
app.config['SERIAL_STOPBITS'] = 1

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///beveragebot.sqlite3'

db = SQLAlchemy(app)
socketio = SocketIO(app, async_mode="eventlet")
ser = Serial(app)

maxDrinks = 6

class drinkList(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    code = db.Column(db.UnicodeText)
    desc = db.Column(db.String(200))
    numPours = db.Column(db.Integer, default=0)
    fav = db.Column(db.Boolean, default=False)
    color = db.Column(db.String(200))

    def __init__(self, name, code, desc, color):
        self.name = name
        self.code = code
        self.desc = desc
        self.color = color




class pourLog(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    code = db.Column(db.UnicodeText)
    pourSize = db.Column(db.Integer)
    batchNum = db.Column(db.Integer)

# def __init__(self, name, city, addr,pin):
#   self.name = name
#   self.city = city
#   self.addr = addr
#   self.pin = pin

class tapList(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    # refers to physical tap, if unavailable do -1
    source = db.Column(db.String(100))
    # refers to code name identifier
    name = db.Column(db.String(100), unique=True)
    display = db.Column(db.String(100))  # refers to display name
    refillDate = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    capacity = db.Column(db.Float)  # quantity in mL
    poured = db.Column(db.Float)  # quantity in mL
    # can this drink be poured (false if out or if not on tap)
    available = db.Column(db.Boolean)

    def __init__(self, source, name, display, capacity, poured, available):
        self.source = source
        self.name = name
        self.display = display
        self.capacity = capacity
        self.poured = poured
        self.available = available

class motorList(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    # refers to electrical motor/valve tap0/1/2/3/4
    source = db.Column(db.String(100), unique=True)
    # is the motor a drink motor, false for ice and tray motor
    isDrink = db.Column(db.Boolean)
    # refers to code name identifier
    calTime = db.Column(db.Float)
    calVol = db.Column(db.Float)  # refers to display name

    def __init__(self, source, isDrink, calTime, calVol):
        self.source = source
        self.isDrink = isDrink
        self.calTime = calTime
        self.calVol = calVol


@app.route("/")
def main():
    taps = db.session.query(tapList).filter(tapList.available == True).all()
    drinksFav = db.session.query(drinkList).filter(drinkList.fav == True).all()
    drinks = db.session.query(drinkList).order_by(drinkList.fav.desc()).all()
    return render_template('home.html', drinks=drinks, drinksFav = drinksFav, taps=taps, maxDrinks=maxDrinks)


@app.route("/drinks")
def drinks():
    #test = drinkList("Coke with Lime", "h20: 0.7, coke: 0.25, lime: 0.05", "Just Coca Cola")
    #db.session.add(test)
    #db.session.commit()
    
    taps = db.session.query(tapList).all()
    tapNames = {}
    for tap in taps:
        tapNames[tap.name] = tap.display
    drinks = db.session.query(drinkList).order_by(drinkList.fav.desc()).all()
    return render_template('drinks.html', drinks=drinks, tapNames=tapNames)

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
            newDrink = drinkList(result["dname"], ", ".join(drinkCode), result["ddesc"], result["color"])
            db.session.add(newDrink)
            db.session.commit()
            #taps = db.session.query(tapList).all()
            #return render_template('drinks.create.html', taps=taps, result = result)
            flash('Successfully created ' + result['dname'], 'success')
            return redirect(url_for('drinks'))
    else:
        taps = db.session.query(tapList).all()
        return render_template('drinks.create.html', taps=taps, result = {})

@app.route("/drinks/delete/<id>", methods = ['POST', 'GET'])
def drinksDelete(id):
    name = db.session.query(drinkList).filter(drinkList.id == id).first().name
    db.session.query(drinkList).filter(drinkList.id == id).delete()
    db.session.commit()
    flash('Successfully deleted ' + name, 'info')
    return redirect(url_for('drinks'))

@app.route("/drinks/fav/<id>", methods = ['POST', 'GET'])
def drinksFav(id):
    name = db.session.query(drinkList).filter(drinkList.id == id).first().name
    isFav = db.session.query(drinkList).filter(drinkList.id == id).first().fav
    db.session.query(drinkList).filter(drinkList.id == id).first().fav = not isFav
    db.session.commit()
    prefix = ""
    if isFav:
        prefix = "un"
    flash('Successfully '+ prefix +'favorited ' + name, 'info')
    return redirect(url_for('drinks'))

@app.route("/taplist")
def taplist():
    # Creation Example
    #test = tapList("tap4", "van", "Vanilla Syrup", "200", "0", True)
    #db.session.add(test)
    #db.session.commit()
    taps = db.session.query(tapList).filter(tapList.source != "none").order_by(tapList.source.asc()).all()
    taps.extend(db.session.query(tapList).filter(tapList.source == "none").order_by(tapList.display.asc()).all())
    now = datetime.datetime.now()
    return render_template('taplist.html', taps=taps, now=now)

@app.route("/taplist/edit/<string:name>", methods = ['POST', 'GET'])
def tapEdit(name):
    #db.session.add(motorList("tap0", True, 0, 0))
    #db.session.add(motorList("tap1", True, 0, 0))
    #db.session.add(motorList("tap2", True, 0, 0))
    #db.session.add(motorList("ice", False, 0, 0))
    #db.session.add(motorList("tray", False, 0, 0))
    #db.session.commit()
    if request.method == 'POST':
        result = request.form
        id = db.session.query(tapList).filter(tapList.name == name).first().id
        db.session.query(tapList).filter(tapList.id == id).first().name = result["name"]
        db.session.query(tapList).filter(tapList.id == id).first().display = result["display"]
        db.session.query(tapList).filter(tapList.id == id).first().capacity = float(result["capacity"])
        db.session.query(tapList).filter(tapList.id == id).first().poured = float(result["poured"])
        db.session.query(tapList).filter(tapList.id == id).first().source = result["tapSrc"]
        db.session.query(tapList).filter(tapList.id == id).first().available = not bool(float(result["poured"]) == float(result["capacity"]) or result["tapSrc"] == "none")
        print(bool(float(result["poured"]) == float(result["capacity"]) or result["tapSrc"] == "none"))
        print(bool(float(result["poured"]) == float(result["capacity"])))
        print(bool(result["tapSrc"] == "none"))
        db.session.commit()
        flash('Successfully modified ' + result['display'], 'success')
        return redirect(url_for('taplist'))
    else:
        info = db.session.query(tapList).filter(tapList.name == name).first()
        mL = db.session.query(motorList).filter(motorList.isDrink == True).all()
        return render_template('./tap.edit.html', tap=info, motorList=mL)


@app.route("/taplist/refill/<string:name>")
def tapRefill(name):
    id = db.session.query(tapList).filter(tapList.name == name).first().id
    display = db.session.query(tapList).filter(tapList.name == name).first().display
    db.session.query(tapList).filter(tapList.id == id).first().poured = 0
    db.session.query(tapList).filter(tapList.id == id).first().refillDate = datetime.datetime.now()
    db.session.query(tapList).filter(tapList.id == id).first().available = True
    db.session.commit()
    flash('Successfully refilled ' + display, 'success')
    return redirect(url_for('taplist'))





@app.route("/manage")
def manage():
    return render_template('manage.html')


@app.route("/calibrate")
def calibrate():
    ml = db.session.query(motorList).all()
    return render_template('calibrate.html', ml=ml)

@app.route("/calibrate/<string:name>")
def calibrateSrc(name):
    ml = db.session.query(motorList).filter(motorList.source == name).all()
    print(ml)
    return render_template('calibrate.source.html', m=ml[0])


@socketio.on('connect')
def test_connect():
    emit('my response', {'data': 'Connected'})
    return

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')
    return

@app.route("/serial")
def serialConnection():
    return render_template('serial.html')

@socketio.on('send')
def handle_send(json_str):
    data = json.loads(json_str)
    ser.on_send(data['message'] + '\r\n')
    print("send to serial: %s"%data['message'])
    return

@socketio.on('pour')
def handle_send(json_str):
    data = json.loads(json_str)
    #ser.on_send(data['message'] + '\r\n')
    print("recieved pour order: %s"%json_str)
    pourDrinks(data);
    return

def pourDrinks(data):
    for d in data: # Drink Pouring Logic. NON BLOCKING
        #   d['name']  d['code']    d['ice']
        # pour ice
        pourIce(d['ice'], d['size'])
        time.sleep(5)
        # turn tray
        turnTray(40)
        time.sleep(5)
        # fill drink
        print(d['code'] + '\n' + str(d['size']) + '\n')
        pourDrink(d['code'], d['size'])
        time.sleep(5)
        # turn tray
        turnTray(20)
        time.sleep(1)

    return

@ser.on_message()
def handle_message(msg):
    print("receive a message:", msg)
    socketio.emit("serial_message", data={"message":str(msg)})
    return

@ser.on_log()
def handle_logging(level, info):
   print(level, info)
   return

@socketio.on('pourt')
def handle_send(data):
    print(data)
    source = data[0]
    value = float(data[1])
    #ser.on_send(data['message'] + '\r\n')
    print("recieved pour time: %f"%value)
    #source = db.session.query(tapList).filter(tapList.name == data[0]).first().source
    sendSerial(source + '|' + str(round(value, 3)))
    return


@socketio.on('calibrate')
def handle_send(data):
    source = data[0]
    volume = round(float(data[1]),3)
    time = round(float(data[2]),3)
    print("setting new calibration data")
    db.session.query(motorList).filter(motorList.source == source).first().calTime = time
    db.session.query(motorList).filter(motorList.source == source).first().calVol = volume 
    db.session.commit()       
    return



def pourDrink(code, cupSize):
    print("Pouring drinks")
    #h2o: 0.6363636363636364, coke: 0.2727272727272727, van: 0.09090909090909091
    codeSplit = code.split(", ")
    for i in codeSplit:
        j = i.split(": ")
        source = db.session.query(tapList).filter(tapList.name == j[0]).first().source
        calTime = db.session.query(motorList).filter(motorList.source == source).first().calTime
        calVol = db.session.query(motorList).filter(motorList.source == source).first().calVol
        quantity = float(j[1]) * float(cupSize) / float(calVol) * float(calTime)
        sendSerial(source + "|" + str(round(quantity,3)))
        time.sleep(1)
    return

def turnTray(angle):
    print("Turning tray angle of " + str(angle))
    sendSerial('tray|' + str(angle))
    return

def pourIce(amnt, cupSize):
    calTime = db.session.query(motorList).filter(motorList.source == "ice").first().calTime
    calVol = db.session.query(motorList).filter(motorList.source == "ice").first().calVol
    pourTime = calVol / cupSize * calTime * amnt
    print("Pouring ice for " + str(pourTime))
    sendSerial('ice|' + str(round(pourTime, 3)))
    return


def sendSerial(msg):
    ser.on_send('<' + msg + '>\r\n')
    return


# Example left in case weird url names will be needed


@app.route("/hello/<string:name>/")
def hello(name):
    return render_template(
        './test.html', name=name)


if __name__ == "__main__":
    print("DB CREATE")
    db.create_all()
    print("SOCKETIO RUN")
    socketio.run(app, debug=False)
    #print("FAILED SOCKETIO")
    #app.run(debug=False)
