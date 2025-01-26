import pytest
import requests

# Base URLs for the services
STOCKS_SERVICE_URL = "http://localhost:5001"

# Test data
stock1 = {
    "name": "NVIDIA Corporation",
    "symbol": "NVDA",
    "purchase_price": 134.66,
    "purchase_date": "18-06-2024",
    "shares": 7
}
stock2 = {
    "name": "Apple Inc.",
    "symbol": "AAPL",
    "purchase_price": 183.63,
    "purchase_date": "22-02-2024",
    "shares": 19
}
stock3 = {
    "name": "Alphabet Inc.",
    "symbol": "GOOG",
    "purchase_price": 140.12,
    "purchase_date": "24-10-2024",
    "shares": 14
}
stock4 = {
    "name":"Tesla, Inc.",
    "symbol":"TSLA",
    "purchase price":194.58,
    "purchase date":"28-11-2022",
    "shares":32
}

stock5 = {
    "name":"Microsoft Corporation",
    "symbol":"MSFT",
    "purchase price":420.55,
    "purchase date":"09-02-2024",
    "shares":35
}
stock6 = {
    "name":"Intel Corporation",
    "symbol":"INTC",
    "purchase price":19.15,
    "purchase date":"13-01-2025",
    "shares":10
}
stock7 = {
    "name": "Amazon.com, Inc.",
    "purchase_price": 134.66,
    "purchase_date": "18-06-2024",
    "shares": 7
}
stock8 = {
    "name": "Amazon.com, Inc.",
    "symbol": "AMZN",
    "purchase_price": 134.66,
    "purchase_date": "Tuesday, June 18, 2024",
    "shares": 7
}

@pytest.fixture
def setup_stocks():
    # Clean up before starting tests
    requests.delete(f"{STOCKS_SERVICE_URL}/stocks")
    yield
    # Clean up after tests
    requests.delete(f"{STOCKS_SERVICE_URL}/stocks")

def test_post_stocks(setup_stocks):
    # Test 1: Add 3 stocks and verify IDs and status codes
    response1 = requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock1)
    response2 = requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock2)
    response3 = requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock3)

    assert response1.status_code == 201
    assert response2.status_code == 201
    assert response3.status_code == 201
    assert response1.json()["_id"] != response2.json()["_id"] != response3.json()["_id"]

def test_get_stock_by_id():
    # Test 2: Retrieve stock1 by ID
    response = requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock1)
    stock_id = response.json()["_id"]

    get_response = requests.get(f"{STOCKS_SERVICE_URL}/stocks/{stock_id}")
    assert get_response.status_code == 200
    assert get_response.json()["symbol"] == "NVDA"

def test_get_all_stocks():
    # Test 3: Verify all stocks are retrieved

    response = requests.get(f"{STOCKS_SERVICE_URL}/stocks")
    assert response.status_code == 200
    assert len(response.json()) == 3

def test_get_stock_value():
    # Test 4: Verify stock values and symbols
    response1 = requests.get(f"{STOCKS_SERVICE_URL}/stocks", json=stock1)
    response2 = requests.get(f"{STOCKS_SERVICE_URL}/stocks", json=stock2)
    response3 = requests.get(f"{STOCKS_SERVICE_URL}/stocks", json=stock3)

    stock_id1 = response1.json()["_id"]
    stock_id2 = response2.json()["_id"]
    stock_id3 = response3.json()["_id"]

    sv1 = requests.get(f"{STOCKS_SERVICE_URL}/stock-value/{stock_id1}").json()
    sv2 = requests.get(f"{STOCKS_SERVICE_URL}/stock-value/{stock_id2}").json()
    sv3 = requests.get(f"{STOCKS_SERVICE_URL}/stock-value/{stock_id3}").json()

    assert sv1["symbol"] == "NVDA"
    assert sv2["symbol"] == "AAPL"
    assert sv3["symbol"] == "GOOG"

def test_portfolio_value():
    # Test 5: Verify portfolio value
    response1 = requests.get(f"{STOCKS_SERVICE_URL}/stocks", json=stock1)
    response2 = requests.get(f"{STOCKS_SERVICE_URL}/stocks", json=stock2)
    response3 = requests.get(f"{STOCKS_SERVICE_URL}/stocks", json=stock3)

    sv1 = requests.get(f"{STOCKS_SERVICE_URL}/stock-value/{response1.json()['_id']}").json()["stock_value"]
    sv2 = requests.get(f"{STOCKS_SERVICE_URL}/stock-value/{response2.json()['_id']}").json()["stock_value"]
    sv3 = requests.get(f"{STOCKS_SERVICE_URL}/stock-value/{response3.json()['_id']}").json()["stock_value"]

    portfolio_value = requests.get(f"{STOCKS_SERVICE_URL}/portfolio-value").json()["portfolio_value"]

    assert portfolio_value * 0.97 <= sv1 + sv2 + sv3 <= portfolio_value * 1.03

def test_post_invalid_stock():
    # Test 6: Add an invalid stock (missing 'symbol') and expect 400
    response = requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock7)
    assert response.status_code == 400

def test_delete_stock():
    # Test 7: Delete stock2 and verify the status code
    response = requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock2)
    stock_id = response.json()["_id"]

    delete_response = requests.delete(f"{STOCKS_SERVICE_URL}/stocks/{stock_id}")
    assert delete_response.status_code == 200


def test_get_deleted_stock():
    # Test 8: Ensure deleted stock2 is no longer accessible
    response = requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock2)
    stock_id = response.json()["_id"]

    # Delete the stock first
    requests.delete(f"{STOCKS_SERVICE_URL}/stocks/{stock_id}")

    # Attempt to retrieve the deleted stock
    get_response = requests.get(f"{STOCKS_SERVICE_URL}/stocks/{stock_id}")
    assert get_response.status_code == 404


def test_post_invalid_date():
    # Test 9: Add a stock with an invalid date format
    response = requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock8)
    assert response.status_code == 400
