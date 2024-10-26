#!/usr/bin/env python3

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import pandas as pd 
import sqlite3
import os 
import sys

# Number of movies
MOVIE_COUNT=400

# Read in the data
conn = sqlite3.connect("movieRatings.db")
df = pd.read_csv("./movieReplicationSet.csv")
cursor = conn.cursor()

# Set up the sql database
# df.to_sql(name="movieRatings",con=conn)

# Function to do multiple comparisons
def group_comparison(movie, field, filter, filter1_value, filter2_value):
    
    # Get the data for group1
    query = f"SELECT `{movie}` FROM movieRatings where `{filter}` = {filter1_value} and `{movie}` is not null"
    group1_ratings = pd.read_sql(query, conn)
    
    # Get the dat for group2
    query = f"SELECT `{movie}` FROM movieRatings where `{filter}` = {filter2_value} and `{movie}` is not null"
    group2_ratings = pd.read_sql(query, conn)
    
    # Store the statistics for the movie
    # print(movie)
    # print(stats.ttest_ind(female_ratings, male_ratings))
    ratings_summary_df.loc[ratings_summary_df['movie'] == movie, field] = stats.ttest_ind(group1_ratings, group2_ratings)[1][0]





# Problem 1
# Get the count of ratings for each of the 400 movies
ratings_count = df.iloc[:, :MOVIE_COUNT].notnull().sum()
ratings_sum = df.iloc[:, :MOVIE_COUNT].sum()
ratings_summary_df = pd.DataFrame({
    'count': ratings_count,
    'sum': ratings_sum
})

ratings_summary_df["mean"] = ratings_summary_df["sum"] / ratings_summary_df["count"]
# print(ratings_summary_df)



# Determine whether popular
median = ratings_summary_df["count"].median()
ratings_summary_df = ratings_summary_df.reset_index()
ratings_summary_df.columns = ['movie', 'count', 'sum', 'mean'] 
ratings_summary_df['popular'] = ratings_summary_df['count'] >= median

popular_movies = ratings_summary_df.loc[ratings_summary_df['popular'], 'mean']
unpopular_movies = ratings_summary_df.loc[~ratings_summary_df['popular'], 'mean']

# Copare to see if it is significant
stats.ttest_ind(popular_movies, unpopular_movies)
# pvalue=2.2696530276564846e-52 which is absurdly small


# Problem 2
# Get the median year of the movies
ratings_summary_df["year"] = ratings_summary_df["movie"].str[-5:-1].astype(int)


# Determine whether new - newer than the median
median_year = ratings_summary_df["year"].median()
ratings_summary_df['new'] = ratings_summary_df['year'] >= median_year

new_movies = ratings_summary_df.loc[ratings_summary_df['new'], 'mean']
old_movies = ratings_summary_df.loc[~ratings_summary_df['new'], 'mean']

# Copare to see if it is significant
stats.ttest_ind(new_movies, old_movies)
# pvalue=0.1091814139798275 We keep the null hypothesis




# Create a list of all movies
movies = ratings_summary_df["movie"].tolist()

# Run the list of movies through the fuction
for movie in movies:
    group_comparison(movie, "genders_pvalue", "Gender identity (1 = female; 2 = male; 3 = self-described)",1,2)
    group_comparison(movie, "onlychild_pvalue", "Are you an only child? (1: Yes; 0: No; -1: Did not respond)",1,0)


# Problem 3 and 4
# Pvalue for Shrek
ratings_summary_df[ratings_summary_df["movie"] == "Shrek (2001)"]["genders_pvalue"]
# 0.270875

# Percent of movies that differ by gender
len(ratings_summary_df[ratings_summary_df["genders_pvalue"] < .05]) /MOVIE_COUNT
# 0.31

# Problem 5 and 6
# Pvalue for Lion King
ratings_summary_df[ratings_summary_df["movie"] == "The Lion King (1994)"]["onlychild_pvalue"]
# 0.040267

# Percent of movies that differ by being an only child
len(ratings_summary_df[ratings_summary_df["onlychild_pvalue"] < .05]) /MOVIE_COUNT
# 0.1175




# conn.close()