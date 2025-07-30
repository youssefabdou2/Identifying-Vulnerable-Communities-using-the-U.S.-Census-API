# Identifying Vulnerable Communities using U.S. Census API

This project fetches U.S. Census data using a RESTful API and analyzes county-level statistics to identify communities with high vulnerability levels. It calculates a custom vulnerability score using poverty and employment indicators, and visualizes the results using plots.

## Features

- Retrieves data using an API key.
- Cleans and preprocesses the data.
- Calculates poverty rates and employment metrics.
- Computes a composite vulnerability score.
- Categorizes counties by priority level.
- Identifies outliers using z-scores.
- Visualizes trends using Seaborn and Matplotlib.

## Requirements

- Python 3
- pandas, matplotlib, seaborn, scipy, requests, python-dotenv

