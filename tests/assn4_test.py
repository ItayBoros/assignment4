import pytest
import requests

# Base URLs for the services
STOCKS_SERVICE_URL = "http://localhost:5001"

# Test data
stock1 = {
    "name": "NVIDIA Corporation",
    "symbol": "NVDA",
    "purchase price": 134.66,
    "purchase date": "18-06-2024",
    "shares": 7
}
stock2 = {
    "name": "Apple Inc.",
    "symbol": "AAPL",
    "purchase price": 183.63,
    "purchase date": "22-02-2024",
    "shares": 19
}
stock3 = {
    "name": "Alphabet Inc.",
    "symbol": "GOOG",
    "purchase price": 140.12,
    "purchase date": "24-10-2024",
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
    "purchase price": 134.66,
    "purchase date": "18-06-2024",
    "shares": 7
}
stock8 = {
    "name": "Amazon.com, Inc.",
    "symbol": "AMZN",
    "purchase price": 134.66,
    "purchase date": "Tuesday, June 18, 2024",
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

def test_get_stock_by_id(setup_stocks):
    # Test 2: Retrieve stock1 by ID
    response = requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock1)
    assert response.status_code == 201
    stock_id = response.json()["_id"]

    get_response = requests.get(f"{STOCKS_SERVICE_URL}/stocks/{stock_id}")
    assert get_response.status_code == 200
    assert get_response.json()["symbol"] == "NVDA"

def test_get_all_stocks(setup_stocks):
    # Test 3: Verify all stocks are retrieved
    requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock1)
    requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock2)
    requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock3)

    response = requests.get(f"{STOCKS_SERVICE_URL}/stocks")
    assert response.status_code == 200
    assert len(response.json()) == 3

def test_get_stock_value(setup_stocks):
    # Test 4: Verify stock values and symbols
    response1 = requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock1)
    response2 = requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock2)
    response3 = requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock3)

    stock_id1 = response1.json()["_id"]
    stock_id2 = response2.json()["_id"]
    stock_id3 = response3.json()["_id"]

    sv1 = requests.get(f"{STOCKS_SERVICE_URL}/stock-value/{stock_id1}").json()
    sv2 = requests.get(f"{STOCKS_SERVICE_URL}/stock-value/{stock_id2}").json()
    sv3 = requests.get(f"{STOCKS_SERVICE_URL}/stock-value/{stock_id3}").json()

    assert sv1["symbol"] == "NVDA"
    assert sv2["symbol"] == "AAPL"
    assert sv3["symbol"] == "GOOG"

def test_portfolio_value(setup_stocks):
    # Test 5: Verify portfolio value
    requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock1)
    requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock2)
    requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock3)

    portfolio_response = requests.get(f"{STOCKS_SERVICE_URL}/portfolio-value")
    assert portfolio_response.status_code == 200
    portfolio_value = portfolio_response.json()["portfolio value"]

    # Validate portfolio value is a positive number
    assert portfolio_value > 0

def test_post_invalid_stock(setup_stocks):
    # Test 6: Add an invalid stock (missing 'symbol') and expect 400
    response = requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock7)
    assert response.status_code == 400

def test_delete_stock(setup_stocks):
    # Test 7: Delete stock2 and verify the status code
    response = requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock2)
    assert response.status_code == 201
    stock_id = response.json()["_id"]

    delete_response = requests.delete(f"{STOCKS_SERVICE_URL}/stocks/{stock_id}")
    assert delete_response.status_code == 204

def test_get_deleted_stock(setup_stocks):
    # Test 8: Ensure deleted stock2 is no longer accessible
    response = requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock2)
    assert response.status_code == 201
    stock_id = response.json()["_id"]

    # Delete the stock first
    delete_response = requests.delete(f"{STOCKS_SERVICE_URL}/stocks/{stock_id}")
    assert delete_response.status_code == 204

    # Attempt to retrieve the deleted stock
    get_response = requests.get(f"{STOCKS_SERVICE_URL}/stocks/{stock_id}")
    assert get_response.status_code == 404

def test_post_invalid_date(setup_stocks):
    # Test 9: Add a stock with an invalid date format
    response = requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock8)
    assert response.status_code == 400
