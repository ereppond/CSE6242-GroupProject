from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/preferences")
def preferences():
    return render_template(
        "preferences.html", text="Your top recommendation was Tokyo!"
    )


if __name__ == "__main__":
    app.run(debug=True)
