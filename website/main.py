from flask import Flask, render_template, flash, redirect, session, request, abort
app = Flask(__name__)

@app.route("/")
def main():
    return "Hello World!"

@app.route("/hello/<string:name>/")
def hello(name):
    return render_template(
    './test.html',name=name)

if __name__ == "__main__":
   app.run()

