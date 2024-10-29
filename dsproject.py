#!/usr/bin/env python3

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import pandas as pd 
import sqlite3
import itertools

# Number of movies
MOVIE_COUNT=400

# Read in the data
conn = sqlite3.connect("movieRatings.db")
df = pd.read_csv("./movieReplicationSet.csv")
cursor = conn.cursor()

# Set up the sql database
# df.to_sql(name="movieRatings",con=conn)

def plot_movie_ratings(movie1, movie2, movie1_title, movie2_title, title= ""):
    ratings = np.arange(0.5, 5, 0.5)
    # Calculate histogram data
    movie1_counts, _ = np.histogram(movie1, bins=ratings)
    movie2_counts, _ = np.histogram(movie2, bins=ratings)
    
    movie1_percentages = movie1_counts / len(movie1)
    movie2_percentages = movie2_counts / len(movie2)
    
    # Set width and offset for side-by-side positioning
    width = 0.2
    offset = width / 2
    
    # Plot histograms as bar charts for better control
    plt.bar(ratings[:-1] - offset, movie1_percentages, width=width, color="blue", label=movie1_title, align='center')
    plt.bar(ratings[:-1] + offset, movie2_percentages, width=width, color="orange", label=movie2_title, align='center')
    
    plt.xlabel('Rating')
    plt.ylabel('Frequency')
    plt.title(f'Ratings for {title}')
    plt.xticks(ratings)  # Set x-ticks to exact rating points
    plt.legend()
    plt.show()


# Function to do multiple comparisons
def group_comparison(movie, field, filter, filter1_value, filter2_value, plot_title = ""):
    
    # Get the data for group1
    query = f"SELECT `{movie}` FROM movieRatings where `{filter}` = {filter1_value} and `{movie}` is not null"
    group1_ratings = pd.read_sql(query, conn)
        
    # Get the dat for group2
    query = f"SELECT `{movie}` FROM movieRatings where `{filter}` = {filter2_value} and `{movie}` is not null"
    group2_ratings = pd.read_sql(query, conn)
    
    if plot_title != "":
        plot_movie_ratings(group1_ratings, group2_ratings, "female ratings", "male ratings", plot_title)
    
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

# Compare to see if it is significant
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
    group_comparison(movie, "socialeffect_pvalue", "Movies are best enjoyed alone (1: Yes; 0: No; -1: Did not respond)",1,0)
    


# Problem 3 and 4
# Pvalue for Shrek
ratings_summary_df[ratings_summary_df["movie"] == "Shrek (2001)"]["genders_pvalue"]
# 0.270875
group_comparison("Shrek (2001)", "genders_pvalue", "Gender identity (1 = female; 2 = male; 3 = self-described)",1,2,plot_title="Shrek by Gender")

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

# Problem 7 and 8
# Pvalue for Shrek
ratings_summary_df[ratings_summary_df["movie"] == "The Wolf of Wall Street (2013)"]["socialeffect_pvalue"]
# 0.117389

# Percent of movies that differ by gender
len(ratings_summary_df[ratings_summary_df["socialeffect_pvalue"] < .05]) /MOVIE_COUNT
# 0.08

# Problem 9
    
# Get the data for group1
alone = "Home Alone (1990)"
nemo = "Finding Nemo (2003)"
query = f"SELECT `{alone}`, `{nemo}` FROM movieRatings where `{alone}` is not null and `{nemo}` is not null"
alone_nemo_ratings = pd.read_sql(query, conn)

query = f"SELECT `{alone}` FROM movieRatings where `{alone}` is not null"
alone_ratings = pd.read_sql(query, conn)
query = f"SELECT `{alone}`, `{nemo}` FROM movieRatings where `{nemo}` is not null"
nemo_ratings = pd.read_sql(query, conn)

# KS test on alone vs nemo
stats.kstest(alone_nemo_ratings[alone], alone_nemo_ratings[nemo])
# pvalue=2.2038507937682687e-10 so the distributions are not different
stats.kstest(alone_ratings[alone], nemo_ratings[nemo])
# pvalue=6.379397182836346e-10

plot_movie_ratings(alone_nemo_ratings[alone],alone_nemo_ratings[nemo],"Home Alone", "Finding Nemo", "Home Alone / Finding Nemo (Row Elimination)")
plot_movie_ratings(alone_ratings[alone],nemo_ratings[nemo],"Home Alone", "Finding Nemo", "Home Alone / Finding Nemo (Element Elimination)")

# Problem 10
# Get the Star Wars movies
# starwars = [movie for movie in movies if "Star Wars" in movie]
# print(starwars)

# starwars_filter = ""
# starwars_columns = ""
# for i in range(len(starwars)):
#     if i == 0:
#         starwars_filter += f"`{starwars[i]}` is not null"
#         starwars_columns += f"`{starwars[i]}`"
#     else:
#         starwars_filter += f" and `{starwars[i]}` is not null"
#         starwars_columns +=  f", `{starwars[i]}`"
        
# print(starwars_filter)
# print(starwars_columns)
        
# query = f"SELECT {starwars_columns} FROM movieRatings where {starwars_filter}" 
# starwars_ratings = pd.read_sql(query, conn)

# # Perform KS tests for all pairs of columns
# results = []

# # Get all combinations of columns
# column_pairs = itertools.combinations(starwars_ratings.columns, 2)

# for col1, col2 in column_pairs:
#     ks_stat, p_value = stats.ks_2samp(starwars_ratings[col1], starwars_ratings[col2])
#     results.append({
#         'col1': col1,
#         'col2': col2,
#         'ks_stat': ks_stat,
#         'p_value': p_value
#     })

# # Create a DataFrame to display results
# results_df = pd.DataFrame(results)


def series_comparison(series_name):
    series_list = [movie for movie in movies if series_name in movie]
    # print(harrypotter)

    filter = ""
    columns = ""
    for i in range(len(series_list)):
        if i == 0:
            filter += f"`{series_list[i]}` is not null"
            columns += f"`{series_list[i]}`"
        else:
            filter += f" and `{series_list[i]}` is not null"
            columns +=  f", `{series_list[i]}`"
            
    # print(starwars_filter)
    # print(starwars_columns)
            
    query = f"SELECT {columns} FROM movieRatings where {filter}" 
    ratings = pd.read_sql(query, conn)

    # Perform KS tests for all pairs of columns
    results = []

    # Get all combinations of columns
    column_pairs = itertools.combinations(ratings.columns, 2)

    for col1, col2 in column_pairs:
        ks_stat, p_value = stats.ks_2samp(ratings[col1], ratings[col2])
        results.append({
            'col1': col1,
            'col2': col2,
            'ks_stat': ks_stat,
            'p_value': p_value
        })

    # Create a DataFrame to display results
    return pd.DataFrame(results)
    

comparison_star = series_comparison("Star Wars")
comparison_harry = series_comparison("Harry Potter")
comparison_matrix = series_comparison("The Matrix")
comparison_indiana = series_comparison("Indiana Jones")
comparison_jurassic = series_comparison("Jurassic Park")
comparison_pirates = series_comparison("Pirates of the Caribbean")
comparison_toy = series_comparison("Toy Story")
comparison_batman = series_comparison("‘Batman’")



# starwars_dict = {}
        
# for i in range(len(starwars)):
#     starwars_dict[f'sw{i+1}'] = movie

# query = f"SELECT `{alone}` FROM movieRatings where `{alone}` is not null"
# alone_ratings = pd.read_sql(query, conn)
# query = f"SELECT `{alone}`, `{nemo}` FROM movieRatings where `{nemo}` is not null"
# nemo_ratings = pd.read_sql(query, conn)
        
# p_values_starwars = []
# for (i, group1), (j, group2) in itertools.combinations(enumerate(groups), 2):
#     ks_stat, p_value = stats.ks_2samp(group1, group2)
#     p_values.append((f"Group {i+1} vs Group {j+1}", p_value))





# conn.close()