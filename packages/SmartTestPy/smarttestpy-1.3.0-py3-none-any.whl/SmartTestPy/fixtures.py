from typing import Dict, Any
import pytest
from faker import Faker

fake = Faker('pt_BR')  # Configurando para português do Brasil

# 🎭 Fixtures Reutilizáveis para pytest


@pytest.fixture
def fake_user() -> Dict[str, str]:
    """
    Gera um usuário fake para testes.

    Returns:
        Dict[str, str]: Dicionário contendo dados do usuário fake.
    """
    return {
        "name": fake.name(),
        "email": fake.email(),
        "address": fake.address(),
        "phone_number": fake.phone_number(),
        "birthdate": fake.date_of_birth().isoformat(),
    }


@pytest.fixture
def fake_company() -> Dict[str, str]:
    """
    Gera uma empresa fake para testes.

    Returns:
        Dict[str, str]: Dicionário contendo dados da empresa fake.
    """
    return {
        "company_name": fake.company(),
        "catch_phrase": fake.catch_phrase(),
        "address": fake.address(),
        "website": fake.url(),
    }


@pytest.fixture
def mock_response_200() -> Any:
    """
    Mock de resposta HTTP 200 para testes de API.

    Returns:
        Any: Objeto mock com status_code 200 e text "OK".
    """
    class MockResponse:
        def __init__(self) -> None:
            self.status_code = 200
            self.text = "OK"

    return MockResponse()


@pytest.fixture
def fake_product() -> Dict[str, Any]:
    """
    Gera um produto fake para testes de e-commerce.

    Returns:
        Dict[str, Any]: Dicionário contendo dados do produto fake.
    """
    return {
        "product_name": fake.word(),
        "price": round(fake.pyfloat(left_digits=2, right_digits=2, positive=True), 2), # noqa501
        "description": fake.sentence(),
        "created_at": fake.date_time_this_year().isoformat(),
    }


# 🌟 Exemplos rápidos de uso
if __name__ == "__main__":
    print("🧪 Usuário fake:", fake_user())
    print("🏢 Empresa fake:", fake_company())
    print("🛒 Produto fake:", fake_product())
