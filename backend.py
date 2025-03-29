from flask import Flask, render_template, request, jsonify
import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True  # ✅ Auto-reload templates for development

# Route to serve the main HTML file
@app.route('/')
def home():
    return render_template('index.html')

# Function to fetch historical stock data from Yahoo Finance
def get_stock_data(stock_symbol):
    """Fetch historical stock data from Yahoo Finance."""
    stock = yf.Ticker(stock_symbol)
    df = stock.history(period="5y")
    return df

# Function to prepare data for training
def prepare_data(df):
    """Prepare stock data for training."""
    df = df[['Close']].dropna()
    df['Prediction'] = df['Close'].shift(-1)
    df.dropna(inplace=True)

    X = np.array(df[['Close']])
    y = np.array(df['Prediction'])

    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    return X_train, X_test, y_train, y_test, scaler

# Function to train a Random Forest model
def train_model(X_train, y_train):
    """Train a Random Forest model."""
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model

# API endpoint to predict stock prices
@app.route('/predict', methods=['POST'])
def predict():
    """API endpoint to predict stock prices."""
    data = request.json
    stock_symbol = data.get("stock_symbol")

    if not stock_symbol:
        return jsonify({"error": "Stock symbol is required"}), 400

    df = get_stock_data(stock_symbol)
    if df.empty:
        return jsonify({"error": "Invalid stock symbol or no data available"}), 404

    X_train, X_test, y_train, y_test, scaler = prepare_data(df)
    model = train_model(X_train, y_train)

    latest_price = np.array([df['Close'].iloc[-1]]).reshape(-1, 1)
    latest_price_scaled = scaler.transform(latest_price)

    predicted_price = model.predict(latest_price_scaled)[0]

    return jsonify({
        "stock_symbol": stock_symbol,
        "predicted_price": round(predicted_price, 2)
    })

# Run the Flask app
if __name__ == '__main__':
    # ✅ Correct host and port with debug enabled
    app.run(host='0.0.0.0', port=5000, debug=True)
