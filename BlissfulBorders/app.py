from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/preferences")
def preferences():
    return render_template("preferences.html")


@app.route("/add-rating")
def add_rating():
    return render_template("add-rating.html")


if __name__ == "__main__":
    app.run(debug=True, host="http://127.0.0.1", port=5000)
