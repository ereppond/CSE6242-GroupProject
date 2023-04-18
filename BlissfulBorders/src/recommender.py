import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class CollaborativeFilteringRecommender:
    def __init__(self, user_data, location_data):
        self.user_data = user_data
        self.location_data = location_data
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
        self.wpsi_col = "WPSI_rank"
        self.freedom_col = "freedom_rank"
        self.gdp_col = "GDP_rank"
        self.user_item_matrix = None
        self.similarity_matrix = None
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
        return np.where(self.get_user_col() == user_id)[0][0]

    def get_user_col(self):
        return self.get_user_item_matrix().index.values

    def get_item_col(self):
        return self.get_user_item_matrix().columns.values

    def recommend_items(self, user_id, n=5):
        user_index = self.get_user_index(user_id)
        user_item_matrix = self.get_user_item_matrix()
        similarity_matrix = self.get_similarity_matrix()
        weighted_sum = np.zeros(user_item_matrix.shape[1])
        similarity_sum = np.zeros(user_item_matrix.shape[1])
        for index, rating in user_item_matrix.iloc[user_index].iteritems():
            if rating == 0:
                continue
            item_index = np.where(self.get_item_col() == index)[0][0]
            similar_users = similarity_matrix[user_index].argsort()[::-1][1:]
            similar_users_rating = user_item_matrix.iloc[similar_users, item_index]
            similar_users_similarity = similarity_matrix[user_index][similar_users]
            weighted_sum[item_index] = (
                similar_users_rating * similar_users_similarity
            ).sum()
            similarity_sum[item_index] = similar_users_similarity.sum()
        ranking = weighted_sum / similarity_sum
        ranking = pd.DataFrame({"location_id": self.get_item_col(), "ranking": ranking})
        ranking = ranking.sort_values(by="ranking", ascending=False)
        return ranking

    def recommend_places_to_live(self, user_id, n=5):
        recommendations = self.recommend_items(user_id, n=n)
        recommended_places = []
        for index, row in recommendations.iloc[: int(n)].iterrows():
            location = row[self.location_col]
            print(location)
            place = (
                self.location_data[self.location_data[self.location_col] == location]
                .reset_index(drop=True)
                .iloc[0]
            )
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
                "WPSI_rank": place[self.wpsi_col],
                "freedom_rank": place[self.freedom_col],
                "GDP_rank": place[self.gdp_col],
                "recommendation_score": row["ranking"],
            }
            recommended_places.append(place_info)
        return pd.DataFrame(recommended_places)

    def get_new_user_rec(self, user, num_results):
        user_id = self.user_data.shape[0]
        user["user_id"] = user_id
        self.user_data = pd.concat(
            [self.user_data, pd.DataFrame([user])], axis=0
        ).reset_index(drop=True)
        return self.recommend_places_to_live(user_id=user_id, n=num_results)
