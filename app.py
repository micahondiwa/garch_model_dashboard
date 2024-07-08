import streamlit as st
import sqlite3
from config import settings
from data import AlphaVantageAPI, SQLRepository
from model import GarchModel

# Title and description
st.title("Stock Volatility Prediction App")
st.write("This app uses the AlphaVantage API to fetch stock data and GARCH models to predict stock volatility.")

# Inputs
st.sidebar.header("Input Parameters")
ticker = st.sidebar.text_input("Ticker Symbol", value="AAPL")
use_new_data = st.sidebar.checkbox("Fetch New Data", value=True)
n_observations = st.sidebar.number_input("Number of Observations", min_value=1, max_value=10000, value=1000)
p = st.sidebar.number_input("GARCH(p)", min_value=1, max_value=10, value=1)
q = st.sidebar.number_input("GARCH(q)", min_value=1, max_value=10, value=1)
n_days = st.sidebar.number_input("Prediction Horizon (days)", min_value=1, max_value=100, value=5)

# Fetch data button
if st.sidebar.button("Fetch Data"):
    api = AlphaVantageAPI()
    data = api.get_daily(ticker=ticker)
    st.write("Data fetched successfully")
    st.write(data.head())

# Fit model button
if st.sidebar.button("Fit Model"):
    connection = sqlite3.connect(settings.db_name, check_same_thread=False)
    repo = SQLRepository(connection=connection)
    model = GarchModel(ticker=ticker, repo=repo, use_new_data=use_new_data)
    model.wrangle_data(n_observations=n_observations)
    model.fit(p=p, q=q)
    model_path = model.dump()
    st.write(f"Model trained and saved to {model_path}")

# Predict button
if st.sidebar.button("Predict Volatility"):
    connection = sqlite3.connect(settings.db_name, check_same_thread=False)
    repo = SQLRepository(connection=connection)
    model = GarchModel(ticker=ticker, repo=repo, use_new_data=False)
    model.load()
    forecast = model.predict_volatility(horizon=n_days)
    st.write(f"Volatility forecast for the next {n_days} days:")
    st.write(forecast)
