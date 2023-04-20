#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np


def load_data():
    # World Happiness Data
    wh_data = pd.read_csv(
        "https://raw.githubusercontent.com/joannarashid/cse6242_proj/main/WH_data_2019.csv"
    )

    # Women's Prosperity Index
    wps_data = pd.read_csv(
        "https://raw.githubusercontent.com/joannarashid/cse6242_proj/main/WPS-Index-2021-Data.csv",
        encoding="unicode_escape",
    )

    # Tropical Climate Data
    tropical_data = pd.read_csv(
        "https://raw.githubusercontent.com/joannarashid/cse6242_proj/main/tropical_countries.csv"
    )

    # Climate Data
    climate_data = pd.read_csv(
        "https://raw.githubusercontent.com/joannarashid/cse6242_proj/main/climate_zones.csv"
    )

    # LGBTQ Safety and Welfare Data
    lgbtq_data = pd.read_csv(
        "https://raw.githubusercontent.com/joannarashid/cse6242_proj/main/LGBTQ_Safety_Index.csv"
    )

    # Industry Sector Data
    sector_data = pd.read_csv(
        "https://raw.githubusercontent.com/joannarashid/cse6242_proj/main/country_sectors.csv"
    )

    # City Climate Data
    city_data = pd.read_csv(
        "https://raw.githubusercontent.com/ereppond/CSE6242-GroupProject/main/BlissfulBorders/data/city_data.csv"
    )

    aq_data = pd.read_csv(
        "https://raw.githubusercontent.com/ereppond/CSE6242-GroupProject/main/BlissfulBorders/data/SEDAC_annual_pm2-5_concentration.csv"
    )
    wh_data, wps_data, climate_data, lgbtq_data, sector_data = clean_data(
        wh_data, wps_data, climate_data, lgbtq_data, sector_data
    )
    df = join_data(
        wh_data, wps_data, climate_data, lgbtq_data, sector_data, city_data, aq_data
    )
    df = transform_values(df)
    return df


def load_saved_data():
    return pd.read_csv(
        "https://raw.githubusercontent.com/ereppond/CSE6242-GroupProject/main/BlissfulBorders/data/location_data.csv"
    )


def load_user_data():
    return pd.read_csv("data/user_data.csv")


def clean_data(wh_data, wps_data, climate_data, lgbtq_data, sector_data):
    # Clean World Happiness Data (preserving all vars)
    wh_data.rename(
        columns={
            "Overall rank": "WH Rank",
            "Country or region": "Country",
            "Score": "WH Score",
        },
        inplace=True,
    )

    # Clean Women's Prosperity Index Data
    wps_data.rename(
        columns={
            "ï»¿WPS Index rank": "WPS Rank",
            "WPS Index score": "WPS Score",
            "Country": "WPS Country",
        },
        inplace=True,
    )
    wps_data = wps_data.iloc[:, 0:3]  # select vars

    # Clean climate data
    climate_data.rename(columns={"Country": "Climate Country"}, inplace=True)
    climate_data["Climate Country"] = climate_data[
        "Climate Country"
    ].str.strip()  # removing leading spaces

    # Clean LGBTQ data
    lgbtq_data.rename(
        columns={
            "Rank": "LGBTQ Rank",
            "Score \n(worst is -100)\n(best is 0)": "LGBTQ Score",
            "Grade": "LGBTQ Grade",
            "Country": "LGBTQ Country",
        },
        inplace=True,
    )
    lgbtq_data = lgbtq_data[
        ["LGBTQ Rank", "LGBTQ Country", "LGBTQ Score", "LGBTQ Grade"]
    ]

    # Clean sector data
    sector_data.rename(
        columns={"Country": "Sector Country", "dom_sector": "sector"}, inplace=True
    )
    sector_data["Sector Country"] = sector_data[
        "Sector Country"
    ].str.strip()  # removing leading spaces

    return wh_data, wps_data, climate_data, lgbtq_data, sector_data


def join_data(
    wh_data, wps_data, climate_data, lgbtq_data, sector_data, city_data, aq_data
):
    ### Join Data ###

    # since the World Happiness Index is the objectove value for this application,
    # wh_data is the left df on whihc the df is started which ensures all countries in the WHI are included
    # subsequent joins eliminate observations that are not in the WHI

    # merge city_data with World Happiness
    df = city_data.merge(wh_data, how="left", left_on="country", right_on="Country")

    # merge Women's Prosperity df
    df = df.merge(wps_data, how="left", left_on="country", right_on="WPS Country")

    # merge LGBTQ data with main df
    df = df.merge(lgbtq_data, how="left", left_on="country", right_on="LGBTQ Country")

    # merge climate type data with main df
    df = df.merge(
        climate_data, how="left", left_on="country", right_on="Climate Country"
    )

    # merge economic sector data data with main df
    df = df.merge(sector_data, how="left", left_on="country", right_on="Sector Country")

    # merge air quality data
    df = df.merge(
        aq_data,
        how="left",
        left_on=["city_ascii", "Country"],
        right_on=["NAME", "COUNTRYENG"],
    )

    # drop duplicate columns
    df.drop(
        [
            "Climate Country",
            "WPS Country",
            "Avg_temp_F",
            "Avg_temp_C",
            "Sector Country",
            "WPS Country",
            "Sector Country",
            "Sector Country",
        ],
        axis=1,
        inplace=True,
    )
    df["avg_temp"] = df["avg_temp"].round(1)
    df["population"] = df["population"].fillna(0).astype(int)
    return df


### Transform Values ###
climate_zones = {
    "DFC": ["Subartic, severe winter, no dry season, cool summer", "Cold"],
    "CFB": ["Marine west coast, warm summer", "Temperate"],
    "ET": ["Tundra", "Cold"],
    "DFB": ["Humid continental, no dry season, warm summer", "Cold"],
    "BWH": ["Subtropical desert", "Arid"],
    "BSH": ["Subtropical steppe", "Arid"],
    "CFA": ["Humid subtropical, no dry season", "Temperate"],
    "CSA": ["Mediterranean, hot summer", "Temperate"],
    "BSK": ["Mid-latitude steppe", "Arid"],
    "CWB": ["Temperate highland tropical climate with dry winters", "Temperate"],
    "CSB": ["Mediterranean, warm summer", "Temperate"],
    "AM": ["Tropical monsoon", "Tropical"],
    "AW": ["Tropical wet and dry or savanna", "Tropical"],
    "AF": ["Tropical rainforest", "Tropical"],
    "BWK": ["Mid-latitude desert", "Arid"],
    "DWB": ["Humid continental, severe dry winter, warm summer", "Cold"],
    "DSC": ["Humid continental, dry warm summer", "Cold"],
    "CWA": ["Humid subtropical, dry winter", "Temperate"],
    "DSB": ["Humid continental, dry warm summer", "Cold"],
    "DWA": ["Humid continental, severe dry winter, hot summer", "Cold"],
    "DWC": ["Subartic, dry winter, cool summer", "Cold"],
}


def map_climate_zones(zone):
    """
    Maps descriptions found in climate_zones dict to climate code in df per dict
    """
    if zone in climate_zones:
        return climate_zones[zone]
    else:
        return ["", ""]


def categorize_humidity(humidity):
    """
    Maps humidity values to 3 categorical buckets
    """
    if humidity > 60:
        return "Humid"
    elif humidity > 29:
        return "Medium"
    else:
        return "Dry"


def determine_air_quality(value):
    if str(value) == "nan":
        return np.nan
    elif value <= 50:
        return "Good"
    elif 51 <= value <= 100:
        return "Moderate"
    elif 101 <= value <= 150:
        return "Unhealthy for sensitive groups"
    elif 151 <= value <= 200:
        return "Unhealthy"
    elif 201 <= value <= 300:
        return "Very unhealthy"
    else:
        return "Hazardous"


def determine_city_size(value):
    if str(value) == "nan":
        return np.nan
    elif value <= 4999:
        return "Rural"
    elif 5000 <= value <= 99999:
        return "Town"
    elif 100000 <= value <= 299999:
        return "City"
    else:
        return "Big City"


def transform_values(df):
    """
    Caluclulates new values and add column for LGBTQ Score
    Adds new climate zone, climate description, climate type, dominate sector columns
    Calculates normalized (0,1) values for LGBTQ Score, WPS Score, Freedom, and GDP
    """
    # assign int values to LGBTQ letter grades
    grades = list(df["LGBTQ Grade"].unique())
    grades = [grade for grade in grades if type(grade) == str]  # only letter grades
    values = sorted(
        list(range(1, len(grades))), reverse=True
    )  # list of integers in reverse
    scores = dict(zip(grades, values))
    df["LGBTQ Score"] = df["LGBTQ Grade"].apply(
        lambda x: scores.get(x)
    )  # new column with inter values for grades

    # additing climate infomation detail
    climate_codes = df["Climate zone"].unique()

    # apply the mapping function to the climate zone column and create two new columns for descriptions
    df[["Climate description", "Climate type"]] = (
        df["Climate zone"].apply(map_climate_zones).tolist()
    )

    # apply the function to the 'avg_humidity' column and create a new column with the results
    df["humidity"] = df["avg_humidity"].apply(lambda x: categorize_humidity(x))

    # Apply the function to create a new 'air_quality' column
    df["air_quality"] = df["AVPMU_2016"].apply(determine_air_quality)

    # change #2016 aq values to negative for weighted sum calculation
    df["neg_aq"] = df["AVPMU_2016"] * -1

    # Apply the function to create a new 'city_size' column
    df["city_size"] = df["population"].apply(determine_city_size)

    # convert sector data to decimal
    df["Agricultural percent"] = (
        df["Agricultural percent"].str.rstrip("%").astype("float") / 100.0
    )
    df["Industrial percent"] = (
        df["Industrial percent"].str.rstrip("%").astype("float") / 100.0
    )
    df["Service percent"] = (
        df["Service percent"].str.rstrip("%").astype("float") / 100.0
    )

    # add dominant sector
    df["sector"] = df[
        ["Agricultural percent", "Industrial percent", "Service percent"]
    ].idxmax(axis=1)
    df["sector"] = df["sector"].str.replace(" percent", "")

    # Normalizing data to range 0,1
    df["LGBTQ_rank"] = (df["LGBTQ Score"] - df["LGBTQ Score"].min()) / (
        df["LGBTQ Score"].max() - df["LGBTQ Score"].min()
    )
    df["WPS_rank"] = (df["WPS Score"] - df["WPS Score"].min()) / (
        df["WPS Score"].max() - df["WPS Score"].min()
    ).round(3)
    df["freedom_rank"] = (
        df["Freedom to make life choices"] - df["Freedom to make life choices"].min()
    ) / (
        df["Freedom to make life choices"].max()
        - df["Freedom to make life choices"].min()
    )
    df["GDP_rank"] = (df["GDP per capita"] - df["GDP per capita"].min()) / (
        df["GDP per capita"].max() - df["GDP per capita"].min()
    ).round(2)
    df["AQ_rank"] = (df["neg_aq"] - df["neg_aq"].min()) / (
        df["neg_aq"].max() - df["neg_aq"].min()
    ).round(2)

    # apply the function to the 'avg_humidity' column and create a new column with the results
    df["humidity"] = df["avg_humidity"].apply(lambda x: categorize_humidity(x))
    return df


def optimize(df, user_profile, n=5):
    """
    Uses values from user_profile to filter df on users prefered climate, humidity level,
    and dominant economic sector.
    Then uses uses ranked vars in user_profile to calculate weights for each var.
    Column is added to df with weighted value for each var.
    """
    # Filter for climate and sector
    print(df.head())
    df = df[
        (df["climate"] == user_profile["climate"])
        & (df["sector"] == user_profile["sector"])
        & (df["city_size"] == user_profile["city_size"])
    ].copy()

    # Normalize the ranks so that they sum up to 1
    rank_sum = (
        user_profile["LGBTQ_rank"]
        + user_profile["WPSI_rank"]
        + user_profile["freedom_rank"]
        + user_profile["GDP_rank"]
    )
    LGBTQ_weight = user_profile["LGBTQ_rank"] / rank_sum
    WPS_weight = user_profile["WPSI_rank"] / rank_sum
    freedom_weight = user_profile["freedom_rank"] / rank_sum
    GDP_weight = user_profile["GDP_rank"] / rank_sum
    # AQ_weight = user_profile["AQ_rank"] / rank_sum

    # Create a new column in the dataframe that combines the weights with the corresponding variables
    df.loc[:, "weighted_sum"] = (
        (LGBTQ_weight * df["LGBTQ_rank"])
        + (WPS_weight * df["WPSI_rank"])
        + (freedom_weight * df["freedom_rank"])
        + (GDP_weight * df["GDP_rank"])
        # + (AQ_weight) * df["AQ_norm"]
    )

    # Find the top n rows with the highest weighted sums
    try:
        sorted_df = (
            df.sort_values(by="weighted_sum", ascending=False)
            .reset_index(drop=True)
            .head(n)
        )
    except:
        sorted_df = df.sort_values(by=['weighted_sum', 'WH Score'], ascending=False).reset_index(
            drop=True
        )

    # Return a list of the 'City' values of the top n rows
    return sorted_df


if __name__ == "__main__":
    df = load_data()
    # ### User profile ###
    # user_profile = {
    #     "sector": input(
    #         "What economic sector is predominat in you ideal country? ('Agricultural', 'Service', 'Industrial'): "
    #     ),
    #     "climate": input(
    #         "What climate do you prefer? ('Cold', 'Temperate','Tropical'): "
    #     ),
    #     "humidity": input(
    #         "What level of humidity can you tolerate? ('Humid', 'Medium','Dry'): "
    #     ),
    #     "LGBTQ_rank": int(input("Rank the importance of LGBTQ equality from 1 to 4: ")),
    #     "WPSI_rank": int(input("Rank the importance of status of women from 1 to 4: ")),
    #     "freedom_rank": int(
    #         input("Rank the importance of personal freedom from 1 to 4: ")
    #     ),
    #     "GDP_rank": int(
    #         input("Rank the importance of the strength of the economy from 1 to 4: ")
    #     ),
    # }

    # ### Results ###
    # best = optimize(df, user_profile, n=5)

    ### Test Users ###
    user1 = {
        "sector": "Service",
        "climate": "Cold",
        "humidity": "Dry",
        "LGBTQ_rank": 1,
        "WPSI_rank": 2,
        "freedom_rank": 3,
        "GDP_rank": 4,
    }

    user2 = {
        "sector": "Industrial",
        "climate": "Temperate",
        "humidity": "Medium",
        "LGBTQ_rank": 4,
        "WPSI_rank": 3,
        "freedom_rank": 2,
        "GDP_rank": 1,
    }

    user3 = {
        "sector": "Service",
        "climate": "Temperate",
        "humidity": "Humid",
        "LGBTQ_rank": 1,
        "WPSI_rank": 2,
        "freedom_rank": 3,
        "GDP_rank": 4,
    }

    user4 = {
        "sector": "Agricultural",
        "climate": "Tropical",
        "humidity": "Humid",
        "LGBTQ_rank": 3,
        "WPSI_rank": 1,
        "freedom_rank": 2,
        "GDP_rank": 4,
    }

    user1_best = optimize(df, user1, n=5)
    print("User1 5 Best places: ", user1_best)

    user2_best = optimize(df, user2, n=5)
    print("User2 5 Best places: ", user2_best)

    user3_best = optimize(df, user3, n=5)
    print("User3 5 Best places: ", user3_best)

    user4_best = optimize(df, user4, n=5)
    print("User1 5 Best places: ", user4_best)
