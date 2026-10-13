
from datetime import date, timedelta

from fastapi.testclient import TestClient
from backend.main import app
from backend.customers import calculate_package_status

client = TestClient(app)


# Test 1: Check the customer status API

def test_customer_status():
    response = client.get("/api/v1/customers/CUST001/status")

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Customer verification required"
    }



# Test 2: Check an expired package
def test_expired_package():
    expiry_date = date(2020, 1, 1)

    result = calculate_package_status(expiry_date)

    assert result == "expired"


# Test 3: Check an active package
def test_active_package():
    expiry_date = date.today() + timedelta(days=30)

    result = calculate_package_status(expiry_date)

    assert result == "active"


# Test 4: Check a package expiring today
def test_package_expiring_today():
    expiry_date = date.today()

    result = calculate_package_status(expiry_date)

    assert result == "active"


def test_supported_isp():
    from backend.customers import is_supported_isp

    assert is_supported_isp("Falcon") is True
    assert is_supported_isp("Jazz") is True
    assert is_supported_isp("CONNECT") is True
    assert is_supported_isp("UnknownISP") is False



def test_isp_case_insensitive():
    from backend.customers import is_supported_isp

    assert is_supported_isp("falcon") is True
    assert is_supported_isp("FALCON") is True
    assert is_supported_isp("jazz") is True
    assert is_supported_isp("JAZZ") is True
    assert is_supported_isp("connect") is True
    assert is_supported_isp("Connect") is True


def test_isp_with_extra_spaces():
    from backend.customers import is_supported_isp

    assert is_supported_isp(" Falcon ") is True
    assert is_supported_isp(" jazz") is True
    assert is_supported_isp("CONNECT ") is True
    assert is_supported_isp(" UnknownISP ") is False



def test_normalize_isp_name():
    from backend.customers import normalize_isp_name

    assert normalize_isp_name(" falcon ") == "Falcon"
    assert normalize_isp_name("JAZZ") == "Jazz"
    assert normalize_isp_name("connect") == "CONNECT"
    assert normalize_isp_name("UnknownISP") == "Unknown"


def test_get_supported_providers():
    response = client.get("/api/v1/providers")

    assert response.status_code == 200
    assert response.json() == {
        "providers": ["Falcon", "Jazz", "CONNECT"],
        "total": 3
    }
