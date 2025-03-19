from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import xgboost as xgb

app = Flask(__name__)
CORS(app)  # Enable CORS to allow frontend communication

# Serve favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

def get_stock_data(stock_symbol):
    """Fetch historical stock data from Yahoo Finance."""
    stock = yf.Ticker(stock_symbol)
    df = stock.history(period="5y")  # Fetch last 5 years of data
    return df

def prepare_data(df):
    """Prepare stock data for training."""
    df = df[['Close']].dropna()
    df['Prediction'] = df['Close'].shift(-1)  # Predict next day's price
    df.dropna(inplace=True)

    X = np.array(df[['Close']])
    y = np.array(df['Prediction'])

    scaler = MinMaxScaler()
    X = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    return X_train, X_test, y_train, y_test, scaler

def train_model(X_train, y_train):
    """Train an advanced XGBoost model."""
    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100)
    model.fit(X_train, y_train)
    return model

# Root route
@app.route('/')
def home():
    return "Flask server is running!"

@app.route('/predict', methods=['POST'])
def predict():
    """API endpoint to predict stock prices."""
    data = request.json
    stock_symbol = data.get("stock_symbol")

    if not stock_symbol:
        return jsonify({"error": "Stock symbol is required"}), 400

    df = get_stock_data(stock_symbol)
    if df.empty:
        return jsonify({"error": "No stock data available"}), 404

    X_train, X_test, y_train, y_test, scaler = prepare_data(df)
    model = train_model(X_train, y_train)

    latest_price = np.array([df['Close'].iloc[-1]]).reshape(-1, 1)
    latest_price_scaled = scaler.transform(latest_price)

    predicted_price = model.predict(latest_price_scaled)[0]

    return jsonify({
        "stock_symbol": stock_symbol,
        "predicted_price": round(predicted_price, 2)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
