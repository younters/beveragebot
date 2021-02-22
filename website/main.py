from flask import Flask, render_template, flash, redirect, session, request, abort
import os
app = Flask(__name__)

@app.route("/")
def main():
    print(os.listdir ())
    print("TEST")
    return render_template('home.html')

@app.route("/hello/<string:name>/")
def hello(name):
    return render_template(
    './test.html',name=name)

if __name__ == "__main__":
   app.run(debug = True)

