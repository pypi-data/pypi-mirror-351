from typing import Dict, Any
import pytest
from faker import Faker

fake = Faker('pt_BR')

@pytest.fixture
def fake_user() -> Dict[str, str]:
    return {
        "name": fake.name(),
        "email": fake.email(),
        "address": fake.address(),
        "phone_number": fake.phone_number(),
        "birthdate": fake.date_of_birth().isoformat(),
    }

@pytest.fixture
def fake_company() -> Dict[str, str]:
    return {
        "company_name": fake.company(),
        "catch_phrase": fake.catch_phrase(),
        "address": fake.address(),
        "website": fake.url(),
    }

@pytest.fixture
def mock_response_200() -> Any:
    class MockResponse:
        def __init__(self) -> None:
            self.status_code = 200
            self.text = "OK"
    return MockResponse()

@pytest.fixture
def fake_product() -> Dict[str, Any]:
    return {
        "product_name": fake.word(),
        "price": round(fake.pyfloat(left_digits=2, right_digits=2, positive=True), 2),
        "description": fake.sentence(),
        "created_at": fake.date_time_this_year().isoformat(),
    } 