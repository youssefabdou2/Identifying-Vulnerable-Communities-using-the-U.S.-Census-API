# Import required libraries
import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from dotenv import load_dotenv

# Set base URL for the Census API
BASE_URL = "https://2eraiuh.dlai.link/api/UScensus"

# Load environment variables from .env file
load_dotenv()

# Retrieve Census API key from environment variables
API_KEY = os.getenv("CENSUS_API_KEY")

# Set API request parameters
params = { 
    "api_key": API_KEY
}

# Make GET request to fetch census data
response = requests.get(BASE_URL, params=params)

# Print response status to verify successful API call
print(response.status_code)

# Parse JSON content from the API response
census_data = response.json()

# Preview a portion of the JSON response
print(f"{census_data}"[:200])

# Convert the JSON data to a pandas DataFrame
census_df = pd.DataFrame(census_data["data"])

# Display data types of each column in the DataFrame
print("Data types:")
print(census_df.dtypes)

# Display first few records in the DataFrame
census_df.head()

# Drop rows with missing values and create a clean copy
census_df_clean = census_df.dropna().copy()

# Convert selected columns to integer type
numeric_columns = [
    "county", "employed_male", "employed_total",
    "female_pop_over_75", "female_pop_under_5", "male_pop_over_75",
    "male_pop_under_5", "population", "poverty_count",
    "poverty_count_female_over_75", "poverty_count_female_under_5",
    "poverty_count_male_over_75", "poverty_count_male_under_5", "state",
    "total_pop_male"
]
for col in numeric_columns:
    census_df_clean[col] = census_df_clean[col].astype("Int64")

# Show updated data types
print("\nData types:")
print(census_df_clean.dtypes)

# Display the first 10 county-state values
census_df_clean["county_state"].head(10)

# Extract and add state name column by splitting the county_state string
state_name = census_df_clean["county_state"].str.split(", ", expand=True)[1]
census_df_clean["state_name"] = state_name

# Check that state_name column was added successfully
census_df_clean[["county_state", "state_name"]].head()

# Calculate poverty-related statistics
census_df_clean["total_poverty_rate"] = census_df_clean["poverty_count"] / census_df_clean["population"]
poverty_count_under_5 = census_df_clean["poverty_count_male_under_5"] + census_df_clean["poverty_count_female_under_5"]
total_pop_under_5 = census_df_clean["male_pop_under_5"] + census_df_clean["female_pop_under_5"]
census_df_clean["under_5_poverty_rate"] = poverty_count_under_5 / total_pop_under_5
poverty_count_over_75 = census_df_clean["poverty_count_male_over_75"] + census_df_clean["poverty_count_female_over_75"]
total_pop_over_75 = census_df_clean["male_pop_over_75"] + census_df_clean["female_pop_over_75"]
census_df_clean["over_75_poverty_rate"] = poverty_count_over_75 / total_pop_over_75

# Show calculated poverty rates
census_df_clean[["total_poverty_rate", "under_5_poverty_rate", "over_75_poverty_rate"]].head()

# Visualize poverty rates across all counties
plt.figure(figsize=(6, 3))
sns.boxplot(data=census_df_clean[["total_poverty_rate", "under_5_poverty_rate", "over_75_poverty_rate"]])
plt.title("Poverty Rates Distribution by Age Group")
plt.xticks(ticks=[0, 1, 2], labels=["Total", "Under 5", "Over 75"], rotation=45)
plt.show()

# Visualize under-5 poverty rates by state
plt.figure(figsize=(12, 6))
sns.boxplot(x="state_name", y="under_5_poverty_rate", data=census_df_clean)
plt.title("Under-5 Poverty Rate Distribution by State")
plt.xticks(rotation=90)
plt.xlabel("State")
plt.ylabel("Under-5 Poverty Rate")
plt.show()

# Import helper functions
import helper_functions

# Compute employment rate for each county
census_df_clean["employment_rate"] = census_df_clean["employed_total"] / census_df_clean["population"]

# Compute under-5 poverty proportion (from total poverty count)
census_df_clean["under_5_poverty_proportion"] = (
    census_df_clean["poverty_count_female_under_5"] +
    census_df_clean["poverty_count_male_under_5"]
) / census_df_clean["poverty_count"]

# Compute composite vulnerability score from multiple indicators
vulnerability_score = (
    0.35 * census_df_clean["total_poverty_rate"] +
    0.40 * census_df_clean["under_5_poverty_proportion"] +
    0.25 * (1 - census_df_clean["employment_rate"])
)

# Normalize vulnerability score manually between 0 and 1
vulnerability_score_normalized = (
    (vulnerability_score - vulnerability_score.min()) /
    (vulnerability_score.max() - vulnerability_score.min())
)

# Scale normalized score to 0–100 and save to DataFrame
census_df_clean["vulnerability_score"] = vulnerability_score_normalized * 100

# Plot histogram of vulnerability score distribution
sns.histplot(census_df_clean["vulnerability_score"])
plt.title("Vulnerability Score Distribution")
plt.xlabel("Vulnerability Score")
plt.show()

# Display top 5 counties with the highest vulnerability score
census_df_clean.sort_values(by="vulnerability_score", ascending=False)[["county_state", "vulnerability_score"]].head()

# Assign quantile-based priority categories from vulnerability scores
priority_score = pd.qcut(
    census_df_clean["vulnerability_score"],
    q=5,
    labels=["Very Low", "Low", "Medium", "High", "Very High"]
)
census_df_clean["priority_score"] = priority_score

# Display first few rows with priority scores assigned
census_df_clean[["county_state", "vulnerability_score", "priority_score"]].head()

# Group and count counties with "Very High" vulnerability per state
very_high_vulnerability = census_df_clean[census_df_clean["priority_score"] == "Very High"][
    ["vulnerability_score", "state_name"]
]
very_high_vulnerability.groupby("state_name").count().sort_values(by="vulnerability_score", ascending=False)

# Calculate z-scores for the poverty count column to detect outliers
census_df_clean["z_score"] = stats.zscore(census_df_clean["poverty_count"])

# Set z-score threshold for identifying outliers
z_score_threshold = 3

# Select counties where poverty count is a high-end outlier
z_score_outliers = census_df_clean[census_df_clean["z_score"] > z_score_threshold]

# Show counties flagged as outliers based on poverty count
z_score_outliers[[
    "county_state", "poverty_count", "total_poverty_rate",
    "under_5_poverty_rate", "priority_score", "z_score"
]]
