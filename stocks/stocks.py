import os
import pymongo
from flask import Flask, jsonify, request
import uuid
from datetime import datetime
import re
import requests

app = Flask(__name__)

# Get the database name from the environment variable
db_name = os.environ.get("MONGO_DB_NAME")

# Check if the value is properly set
if not db_name:
    raise ValueError("Environment variable MONGO_DB_NAME is not set or empty")

# Initialize the MongoDB client and database
client = pymongo.MongoClient("mongodb://mongo:27017/")
db = client[db_name]  # db_name must be a string
inv = db["inventory"]

def genID():
    return str(uuid.uuid4())

def transform_stock(stock):
    if not stock:
        return stock
    stock["id"] = stock.pop("_id")
    return stock

@app.route('/kill', methods=['GET'])
def kill_container():
    os._exit(1)

@app.route('/stocks', methods=['DELETE'])
def delete_all_stocks():
    try:
        inv.delete_many({})
        return '', 204
    except Exception as e:
        return jsonify({"server error": str(e)}), 500
        
@app.route('/stocks', methods=['POST'])
def addStock():
    try:
        content_type = request.headers.get('Content-Type')
        if content_type != 'application/json':
            return jsonify({"error": "Expected application/json media type"}), 415
        data = request.get_json()
        required_fields = ['symbol', 'purchase price', 'shares']

        # Check for malformed data
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Malformed data"}), 400
        
        # Check if symbol is not a string
        if not isinstance(data['symbol'], str):
            return jsonify({"error": "Invalid stock symbol"}), 400
        
        # Check if shares is not a positive integer
        if not isinstance(data['shares'], int) or data['shares'] <= 0:
            return jsonify({"error": "Shares must be a positive integer"}), 400

        # Check if purchase price is not a positive number
        if not isinstance(data['purchase price'], (int, float)) or data['purchase price'] <= 0:
            return jsonify({"error": "Purchase price must be a positive number"}), 400

        # Generate UUID
        new_id = genID()

        # Check if the optional name field is provided and valid
        if 'name' in data:
            if not isinstance(data['name'], str):
                return jsonify({"error": "name must be a string"}), 400
            name = data['name']
        else:
            name = "NA"

        # Check if stock already exists for this account (by symbol)
        doc = inv.find_one({"symbol": data['symbol'].upper()})
        if doc:
            return jsonify({"error": "Stock symbol already exists for this account"}), 400

        # Set optional purchase date field
        purchase_date = data.get('purchase date', "NA")
        if purchase_date != "NA" and not validate_date_format(purchase_date):
            return jsonify({"error": "Invalid date format. Use DD-MM-YYYY"}), 400

        stock = {
            '_id': new_id,
            'name': name,
            'symbol': data['symbol'].upper(),
            'purchase price': round(data['purchase price'], 2),
            'purchase date': purchase_date,
            'shares': data['shares']
        }
        inv.insert_one(stock)
        response_data = {"id": new_id}
        return jsonify(response_data), 201
    except Exception as e:
        return jsonify({"server error": str(e)}), 500

@app.route('/stocks', methods=['GET'])
def getStocks():
    try:
        query = request.args.to_dict()

        for key in query:
            if key == "shares":
                query[key] = int(query[key])  # Convert shares to integer
            elif key == "purchase price":
                query[key] = float(query[key])
        
        # If there are no filters, return all stocks
        if not query:
            all_stocks = list(inv.find())
            # Transform each stock document
            transformed = [transform_stock(stock) for stock in all_stocks]
            return jsonify(transformed), 200

        for field in query.keys():
            if field not in ['id', '_id', 'name', 'symbol', 'shares', 'purchase price', 'purchase date']:
                return jsonify({'error': 'invalid query field'}), 422

        stocks = inv.find(query)
        filtered_stocks = list(stocks)

        if not filtered_stocks:
            return jsonify({"error": "No stocks match the given filters"}), 404

        # Transform each stock document
        transformed = [transform_stock(stock) for stock in filtered_stocks]
        return jsonify(transformed), 200

    except Exception as e:
        return jsonify({"server error": str(e)}), 500

@app.route('/stocks/<string:stockId>', methods=['GET'])
def getStock(stockId):
    try:
        stock = inv.find_one({'_id': stockId})
        if stock is None:
            return jsonify({"error": "No such ID"}), 404
        return jsonify(transform_stock(stock)), 200
    except Exception as e:
        return jsonify({"server error": str(e)}), 500

@app.route('/stocks/<string:stockId>', methods=['DELETE'])
def deleteStock(stockId):
    try:
        stock = inv.find_one({'_id': stockId})
        if not stock:
            return jsonify({"error": "No such ID"}), 404
        resp = inv.delete_one({'_id': stockId})
        if resp.deleted_count == 1:
            return '', 204
    except KeyError:
        return jsonify({"error": "No such ID"}), 404
    except Exception as e:
        return jsonify({"server error": str(e)}), 500

@app.route('/stocks/<string:stockId>', methods=['PUT'])
def updateStock(stockId):
    try:
        content_type = request.headers.get('Content-Type')
        if content_type != 'application/json':
            return jsonify({"error": "expected application/json media type"}), 415
        data = request.get_json()

        required_fields = ['_id', 'name', 'symbol', 'purchase price', 'purchase date', 'shares']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Malformed data"}), 400

        stock = inv.find_one({'_id': stockId})
        if not stock:
            return jsonify({"error": "Not found"}), 404

        # Changing the ID isn't allowed
        if data['_id'] != stock['_id']:
            return jsonify({"error": "Stock ID can not be change"}), 400

        # Changing the symbol isn't allowed
        if not isinstance(data['symbol'], str):
            return jsonify({"error": "Invalid stock symbol"}), 400
        if data['symbol'].upper() != stock['symbol']:
            return jsonify({"error": "Stock symbol can not be change"}), 400

        # Validate shares and purchase price
        if not isinstance(data['shares'], int) or data['shares'] <= 0:
            return jsonify({"error": "Shares must be a positive integer"}), 400
        if not isinstance(data['purchase price'], (int, float)) or data['purchase price'] <= 0:
            return jsonify({"error": "Purchase price must be a positive number"}), 400

        # Validate and set name field
        if stock['name'] == "NA" and data['name'] != "NA":
            if not isinstance(data['name'], str):
                return jsonify({"error": "name must be a string"}), 400
            name = data['name']
        elif stock['name'] != "NA" and data['name'] == "NA":
            name = stock['name']
        else:
            if not isinstance(data['name'], str):
                return jsonify({"error": "name must be a string"}), 400
            name = data['name']

        # Validate and set purchase date field
        if stock['purchase date'] == "NA" and data['purchase date'] != "NA":
            if not validate_date_format(data['purchase date']):
                return jsonify({"error": "Invalid date format. Use DD-MM-YYYY"}), 400
            purchase_date = data['purchase date']
        elif stock['purchase date'] != "NA" and data['purchase date'] == "NA":
            purchase_date = stock['purchase date']
        elif stock['purchase date'] != "NA" and data['purchase date'] != "NA":
            if not validate_date_format(data['purchase date']):
                return jsonify({"error": "Invalid date format. Use DD-MM-YYYY"}), 400
            purchase_date = data['purchase date']
        else:
            purchase_date = stock['purchase date']

        updated_fields = {
            'name': name,
            'purchase price': round(data['purchase price'], 2),
            'purchase date': purchase_date,
            'shares': data['shares']
        }

        inv.update_one({'_id': stockId}, {'$set': updated_fields})
        response_data = {"id": stockId}
        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"server error": str(e)}), 400

def validate_date_format(date_string):
    pattern = r"^\d{2}-\d{2}-\d{4}$"
    if not re.match(pattern, date_string):
        return False
    try:
        datetime.strptime(date_string, "%d-%m-%Y")
        return True
    except ValueError:
        return False

def get_ticker_price(symbol):
    try:
        api_url = f"https://api.api-ninjas.com/v1/stockprice?ticker={symbol}"
        headers = {'X-Api-Key': 'JtneO16sSFCqKQ8bJqYLEA==yqfESh50NJdz5O5Q'}
        response = requests.get(api_url, headers=headers)

        if response.status_code == requests.codes.ok:
            data = response.json()
            return data.get('price')
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

@app.route('/stock-value/<string:stockId>', methods=['GET'])
def get_stock_value(stockId):
    try:
        stock = inv.find_one({'_id': stockId})
        if not stock:
            return jsonify({"error": "Not found"}), 404

        ticker_price = get_ticker_price(stock['symbol'])
        if ticker_price is None:
            return jsonify({"error": "Failed to retrieve ticker price"}), 500

        stock_value = ticker_price * stock['shares']
        return jsonify({
            "symbol": stock['symbol'],
            "ticker": ticker_price,
            "stock value": stock_value
        }), 200

    except Exception as e:
        return jsonify({"server error": str(e)}), 500

@app.route('/portfolio-value', methods=['GET'])
def get_portfolio_value():
    try:
        portfolio_value = 0.0
        stocks = inv.find()
        for stock in stocks:
            ticker_price = get_ticker_price(stock['symbol'])
            if ticker_price is None:
                return jsonify({"error": "Failed to retrieve ticker price"}), 500
            portfolio_value += ticker_price * stock['shares']

        current_date = datetime.now().strftime('%Y-%m-%d')
        return jsonify({
            "date": current_date,
            "portfolio value": portfolio_value
        }), 200

    except Exception as e:
        return jsonify({"server error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
