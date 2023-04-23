from flask import Flask, render_template, request
from src.weighted_sum import load_data, optimize, load_user_data
from src.recommender import CollaborativeFilteringRecommender as rec
import pandas as pd

app = Flask(__name__)

df = load_data()
user_data = load_user_data()

r = rec()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit_form", methods=["POST"])
def submit_form():
    sector = request.form.get("sector")
    climate = request.form.get("climate")
    humidity = request.form.get("humidity")
    city_size = request.form.get("city_size")
    lgbtq = int(request.form.get("lgbtq"))
    women = int(request.form.get("women"))
    freedom = int(request.form.get("freedom"))
    economy = int(request.form.get("economy"))
    num_results = int(request.form.get("num_results"))
    user = {
        "sector": sector,
        "climate": climate,
        "humidity": humidity,
        "city_size": city_size,
        "LGBTQ_rank": lgbtq,
        "WPS_rank": women,
        "freedom_rank": freedom,
        "GDP_rank": economy,
    }

    results = optimize(df, user, n=num_results).reset_index(drop=True)
    if results.shape[0] > 0:
        lat = results.loc[0, "lat"]
        lng = results.loc[0, "lng"]
    else:
        lat = 40.4406
        lng = -79.9959
    filename = "test_results.csv"
    results.to_csv(f"static/{filename}", index=False)
    return render_template(
        "preferences.html",
        filename=filename,
        lat=lat,
        lng=lng,
        popup="If you want to get results based on other users similar to you, try our rating form on the 'Rate My Location' Tab.",
    )


@app.route("/preferences")
def preferences():
    sample = df.copy(deep=True)
    sample = (
        sample[sample["city_size"] == "Big City"]
        .sort_values("wh_rank")
        .reset_index(drop=True)
        .iloc[:20]
    )
    lat = sample.loc[0, "lat"]
    lng = sample.loc[0, "lng"]
    sample.to_csv("static/sample_data.csv", index=False)
    filename = "sample_data.csv"
    return render_template(
        "preferences.html",
        filename=filename,
        lat=lat,
        lng=lng,
        popup="To get real recommendations, enter your preferences under the 'Home' tab.",
    )


@app.route("/add-rating")
def add_rating():
    return render_template("add-rating.html")


@app.route("/submit_rating", methods=["POST"])
def submit_rating():
    city = request.form.get("city")
    country = request.form.get("country")
    rating = request.form.get("rating")
    sector = request.form.get("sector")
    climate = request.form.get("climate")
    humidity = request.form.get("humidity")
    city_size = request.form.get("city_size")
    lgbtq = int(request.form.get("lgbtq"))
    women = int(request.form.get("women"))
    freedom = int(request.form.get("freedom"))
    economy = int(request.form.get("economy"))

    user = {
        "sector": sector,
        "climate": climate,
        "humidity": humidity,
        "city_size": city_size,
        "LGBTQ_rank": lgbtq,
        "WPS_rank": women,
        "freedom_rank": freedom,
        "GDP_rank": economy,
        "city": city,
        "country": country,
        "user_rating": rating,
    }
    location_id = df[(df["city"] == city) & (df["country"] == country)][
        "location_id"
    ].values[0]
    user["location_id"] = location_id
    user_id = r.user_data["user_id"].astype(int).max() + 1
    user["user_id"] = user_id
    results = r.get_new_user_rec(user, 5)
    lat = results.loc[0, "lat"]
    lng = results.loc[0, "lng"]
    filename = "test_results.csv"
    results.to_csv(f"static/{filename}", index=False)
    popup = f"Your UserID is {str(user_id)}. You can now generate recommendations by using the 'Get Results By User ID' tab."
    return render_template(
        "preferences.html", filename=filename, lat=lat, lng=lng, popup=popup
    )


@app.route("/get_user")
def get_user():
    return render_template("results-by-userid.html")


def get_preds(_request, num_results, user):
    if "weighted_filtering" in _request.form:
        results = optimize(df, user, n=num_results).reset_index(drop=True)
    else:
        results = r.recommend_places_to_live(int(user["user_id"]), n=num_results)
    return results


@app.route("/submit_userid", methods=["POST"])
def submit_userid():
    userid = int(request.form.get("userid"))
    num_results = int(request.form.get("num_results"))
    users = pd.read_csv("data/user_data.csv")
    user = users[users["user_id"] == int(userid)].iloc[0]
    results = get_preds(request, num_results, user)
    lat = results.loc[0, "lat"]
    lng = results.loc[0, "lng"]
    filename = "test_results.csv"
    results.to_csv(f"static/{filename}", index=False)
    return render_template("preferences.html", filename=filename, lat=lat, lng=lng)


if __name__ == "__main__":
    app.run(debug=True)  # , host="http://127.0.0.1", port=5000)
