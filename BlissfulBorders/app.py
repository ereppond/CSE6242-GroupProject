from flask import Flask, render_template, request
from src.weighted_sum import *

app = Flask(__name__)

df = load_data()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/test")
def test():
    return render_template("test.html")


@app.route("/submit_form", methods=["POST"])
def submit_form():
    sector = request.form.get("sector")
    climate = request.form.get("climate")
    humidity = request.form.get("humidity")
    lgbtq = int(request.form.get("lgbtq"))
    women = int(request.form.get("women"))
    freedom = int(request.form.get("freedom"))
    economy = int(request.form.get("economy"))
    num_results = int(request.form.get("num_results"))
    user = {
        "sector": sector,
        "climate": climate,
        "humidity": humidity,
        "LGBTQ_rank": lgbtq,
        "WPSI_rank": women,
        "freedom_rank": freedom,
        "GDP_rank": economy,
    }
    results = optimize(df, user, n=num_results)
    filename = "test_results.csv"
    results.to_csv(f"static/{filename}", index=False)
    return render_template("preferences.html", filename=filename)


@app.route("/preferences")
def preferences():
    filename = "sample_data.csv"
    return render_template("preferences.html", filename=filename)


@app.route("/add-rating")
def add_rating():
    return render_template("add-rating.html")


if __name__ == "__main__":
    app.run(debug=True)  # , host="http://127.0.0.1", port=5000)
