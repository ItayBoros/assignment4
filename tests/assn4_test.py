import pytest
import requests

# Base URLs for the services
STOCKS_SERVICE_URL = "http://localhost:5001"
CAPITAL_GAINS_SERVICE_URL = "http://localhost:5003"

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
    assert response1.json()["id"] != response2.json()["id"] != response3.json()["id"]

def test_get_stock_by_id():
    # Test 2: Retrieve stock1 by ID
    response = requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock1)
    stock_id = response.json()["id"]

    get_response = requests.get(f"{STOCKS_SERVICE_URL}/stocks/{stock_id}")
    assert get_response.status_code == 200
    assert get_response.json()["symbol"] == "NVDA"

def test_get_all_stocks():
    # Test 3: Verify all stocks are retrieved
    requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock1)
    requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock2)
    requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock3)

    response = requests.get(f"{STOCKS_SERVICE_URL}/stocks")
    assert response.status_code == 200
    assert len(response.json()) == 3

def test_post_invalid_stock():
    # Test 6: Add an invalid stock (missing 'symbol') and expect 400
    response = requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock7)
    assert response.status_code == 400

def test_delete_stock():
    # Test 7: Delete stock2 and ensure it's gone
    response = requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock2)
    stock_id = response.json()["id"]

    delete_response = requests.delete(f"{STOCKS_SERVICE_URL}/stocks/{stock_id}")
    assert delete_response.status_code == 200

    get_response = requests.get(f"{STOCKS_SERVICE_URL}/stocks/{stock_id}")
    assert get_response.status_code == 404

def test_post_invalid_date():
    # Test 9: Add a stock with an invalid date format
    response = requests.post(f"{STOCKS_SERVICE_URL}/stocks", json=stock8)
    assert response.status_code == 400
