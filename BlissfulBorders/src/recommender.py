import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from src.weighted_sum import load_data


class CollaborativeFilteringRecommender:
    def __init__(self):
        self.user_data = pd.read_csv("data/user_data.csv")
        self.location_data = load_data()
        self.user_col = "user_id"
        self.location_col = "location_id"
        self.city_col = "city"
        self.country_col = "country"
        self.rating_col = "user_rating"
        self.sector_col = "sector"
        self.climate_col = "climate"
        self.humidity_col = "humidity"
        self.city_size_col = "city_size"
        self.lgbtq_col = "LGBTQ_rank"
        self.wpsi_col = "WPS_rank"
        self.freedom_col = "freedom_rank"
        self.gdp_col = "GDP_rank"
        self.user_item_matrix = None
        self.similarity_matrix = None
        # self.user_data = self.user_data.sample(10000)
        self.new_user = False

    def get_user_item_matrix(self):
        if self.user_item_matrix is None:
            merged_data = pd.merge(
                self.user_data, self.location_data, on=self.location_col
            )
            self.user_item_matrix = merged_data.pivot_table(
                index=self.user_col, columns=[self.location_col], values=self.rating_col
            ).fillna(0)
        return self.user_item_matrix

    def get_similarity_matrix(self):
        if self.similarity_matrix is None:
            self.similarity_matrix = cosine_similarity(self.get_user_item_matrix())
        return self.similarity_matrix

    def get_top_similar_users(self, user_id, n=5):
        similarity_matrix = self.get_similarity_matrix()
        user_index = self.get_user_index(user_id)
        similar_users = similarity_matrix[user_index].argsort()[::-1][1 : n + 1]
        return self.get_user_col()[similar_users]

    def get_user_index(self, user_id):
        try:
            return np.where(self.get_user_col() == user_id)[0][0]
        except Exception:
            user = self.get_user_col()[-1]
            return np.where(self.get_user_col() == user)[0][0]

    def get_user_col(self):
        return self.get_user_item_matrix().index.values

    def get_item_col(self):
        return self.get_user_item_matrix().columns.values

    def recommend_items(self, user_id):
        print("Running recommend_items")
        user_index = self.get_user_index(user_id)
        user_item_matrix = self.get_user_item_matrix()
        similarity_matrix = self.get_similarity_matrix()
        weighted_sum = np.zeros(user_item_matrix.shape[1])
        similarity_sum = np.zeros(user_item_matrix.shape[1])

        for index, _ in user_item_matrix.iloc[user_index].iteritems():
            item_index = np.where(self.get_item_col() == index)[0][0]
            similar_users = similarity_matrix[user_index].argsort()[::-1][1:]
            similar_users_rating = user_item_matrix.iloc[similar_users, item_index]
            similar_users_similarity = similarity_matrix[user_index][similar_users]
            weighted_sum[item_index] = (
                similar_users_rating * similar_users_similarity
            ).sum()
            similarity_sum[item_index] = similar_users_similarity.sum()

        ranking = [
            weighted_sum[i] / similarity_sum[i] if similarity_sum[i] != 0 else 0
            for i in range(similarity_sum.shape[0])
        ]
        ranking = pd.DataFrame({"location_id": self.get_item_col(), "ranking": ranking})
        ranking = ranking.sort_values(by="ranking", ascending=False)
        return ranking

    def recommend_places_to_live(self, user_id, n=5):
        print("Running recommend_places_to_live")
        recommendations = self.recommend_items(user_id)
        recommended_places = []
        if recommendations.empty:
            return self.location_data.sort_values(
                by="user_rating", ascending=False
            ).head(n)
        for _, row in recommendations.iloc[: int(n)].iterrows():
            location = row[self.location_col]
            place = (
                self.location_data[self.location_data[self.location_col] == location]
                .reset_index(drop=True)
                .iloc[0]
            )
            users_location = self.user_data[self.user_data["user_id"] == user_id][
                "city"
            ].values
            if place["city"] not in users_location:
                place_info = {
                    "lat": place.lat,
                    "lng": place.lng,
                    "city": place[self.city_col],
                    "country": place[self.country_col],
                    "sector": place[self.sector_col],
                    "climate": place[self.climate_col],
                    "humidity": place[self.humidity_col],
                    "city_size": place[self.city_size_col],
                    "LGBTQ_rank": place[self.lgbtq_col],
                    "WPS_rank": place[self.wpsi_col],
                    "freedom_rank": place[self.freedom_col],
                    "GDP_rank": place[self.gdp_col],
                    "population": place["population"],
                    "air_quality": place["air_quality"],
                    "wh_rank": place["wh_rank"],
                    "recommendation_score": row["ranking"],
                }
                recommended_places.append(place_info)
        recommended_places = pd.DataFrame(recommended_places)
        return recommended_places

    def get_new_user_rec(self, user, num_results):
        self.user_data = pd.concat([self.user_data, pd.DataFrame([user])]).reset_index(
            drop=True
        )
        self.user_data.to_csv("data/user_data.csv", index=False)
        self.user_item_matrix = None
        self.similarity_matrix = None
        self.get_user_item_matrix()
        self.get_similarity_matrix()
        return self.recommend_places_to_live(user_id=user["user_id"], n=num_results)
