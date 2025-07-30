import pytest
from datetime import datetime
from faker import Faker

fake = Faker('pt_BR')

# As fixtures agora estão em tests/conftest.py

# 🧪 Testes para a fixture fake_user
def test_fake_user(fake_user):
    """✅ Testa se a fixture fake_user gera dados válidos."""
    user = fake_user
    assert "name" in user
    assert "email" in user
    assert "address" in user
    assert "phone_number" in user
    assert "birthdate" in user
    assert "@" in user["email"], "❌ E-mail inválido."


# 🏢 Testes para a fixture fake_company
def test_fake_company(fake_company):
    """🏢 Testa se a fixture fake_company gera dados válidos."""
    company = fake_company
    assert "company_name" in company
    assert "catch_phrase" in company
    assert "address" in company
    assert "website" in company
    assert company["website"].startswith("http"), "❌ URL inválida."


# 🛒 Testes para a fixture fake_product
def test_fake_product(fake_product):
    """🛒 Testa se a fixture fake_product gera dados válidos."""
    product = fake_product
    assert "product_name" in product
    assert "price" in product
    assert product["price"] > 0, "❌ Preço deve ser positivo."
    assert "description" in product
    assert "created_at" in product


# ✅ Testes para mock_response_200
def test_mock_response_200(mock_response_200):
    """✅ Testa se a fixture mock_response_200 retorna código 200 e texto OK."""
    response = mock_response_200
    assert response.status_code == 200, "❌ Status code inválido."
    assert response.text == "OK", "❌ Texto da resposta incorreto."


def test_fake_user_structure(fake_user):
    """Testa se o usuário fake tem todos os campos necessários."""
    user = fake_user
    assert isinstance(user, dict)
    assert all(key in user for key in [
        "name", "email", "address", "phone_number", "birthdate"
    ])
    assert isinstance(user["name"], str)
    assert "@" in user["email"]
    assert isinstance(user["address"], str)
    assert isinstance(user["phone_number"], str)
    assert isinstance(user["birthdate"], str)

def test_fake_company_structure(fake_company):
    """Testa se a empresa fake tem todos os campos necessários."""
    company = fake_company
    assert isinstance(company, dict)
    assert all(key in company for key in [
        "company_name", "catch_phrase", "address", "website"
    ])
    assert isinstance(company["company_name"], str)
    assert isinstance(company["catch_phrase"], str)
    assert isinstance(company["address"], str)
    assert isinstance(company["website"], str)
    assert company["website"].startswith(("http://", "https://"))

def test_mock_response_200_structure(mock_response_200):
    """Testa se o mock de resposta HTTP 200 funciona corretamente."""
    response = mock_response_200
    assert hasattr(response, "status_code")
    assert hasattr(response, "text")
    assert response.status_code == 200
    assert response.text == "OK"

def test_fake_product_structure(fake_product):
    """Testa se o produto fake tem todos os campos necessários."""
    product = fake_product
    assert isinstance(product, dict)
    assert all(key in product for key in [
        "product_name", "price", "description", "created_at"
    ])
    assert isinstance(product["product_name"], str)
    assert isinstance(product["price"], float)
    assert 0 < product["price"] < 100
    assert isinstance(product["description"], str)
    assert isinstance(product["created_at"], str)

def test_fake_user_uniqueness(fake_user):
    """Testa se os usuários fake gerados são únicos."""
    user1 = fake_user
    user2 = {
        "name": fake.name(),
        "email": fake.email(),
        "address": fake.address(),
        "phone_number": fake.phone_number(),
        "birthdate": fake.date_of_birth().isoformat(),
    }
    assert user1 != user2

def test_fake_company_uniqueness(fake_company):
    """Testa se as empresas fake geradas são únicas."""
    company1 = fake_company
    company2 = {
        "company_name": fake.company(),
        "catch_phrase": fake.catch_phrase(),
        "address": fake.address(),
        "website": fake.url(),
    }
    assert company1 != company2

def test_fake_product_uniqueness(fake_product):
    """Testa se os produtos fake gerados são únicos."""
    product1 = fake_product
    product2 = {
        "product_name": fake.word(),
        "price": round(fake.pyfloat(left_digits=2, right_digits=2, positive=True), 2),
        "description": fake.sentence(),
        "created_at": fake.date_time_this_year().isoformat(),
    }
    assert product1 != product2

def test_fake_product_price_range():
    """Testa se o preço do produto fake está dentro do intervalo esperado."""
    for _ in range(10):  # Testa múltiplas gerações
        product = {
            "product_name": fake.word(),
            "price": round(fake.pyfloat(left_digits=2, right_digits=2, positive=True), 2),
            "description": fake.sentence(),
            "created_at": fake.date_time_this_year().isoformat(),
        }
        assert 0 < product["price"] < 100
        assert len(str(product["price"]).split(".")[1]) <= 2  # Verifica casas decimais

# 🏃 **Execução dos testes**
if __name__ == "__main__":
    pytest.main(["-v", "tests/test_fixtures.py"])
