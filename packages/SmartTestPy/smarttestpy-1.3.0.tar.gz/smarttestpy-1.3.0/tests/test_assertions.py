import pytest

from SmartTestPy.assertions import (assert_equal_with_message,
                                    assert_in_response, assert_status_code)


# 🔄 Classe mock para simular respostas
class MockResponse:
    def __init__(self, status_code, text=""):
        self.status_code = status_code
        self.text = text


# ✅ Testes para assert_status_code
def test_assert_status_code_success():
    """Testa o caso de sucesso para assert_status_code."""
    response = MockResponse(200, "OK")
    assert_status_code(response, 200)


def test_assert_status_code_failure():
    """Testa o caso de falha para assert_status_code."""
    response = MockResponse(404, "Not Found")
    with pytest.raises(AssertionError) as exc_info:
        assert_status_code(response, 200)
    assert "Código de status inválido" in str(exc_info.value)


# 🔍 Testes para assert_in_response
def test_assert_in_response_success():
    """Testa o caso de sucesso para assert_in_response."""
    response = MockResponse(200, "Hello World")
    assert_in_response(response, "World")


def test_assert_in_response_failure():
    """Testa o caso de falha para assert_in_response."""
    response = MockResponse(200, "Hello World")
    with pytest.raises(AssertionError) as exc_info:
        assert_in_response(response, "Python")
    assert "Conteúdo 'Python' não encontrado" in str(exc_info.value)


# ⚡ Testes para assert_equal_with_message
def test_assert_equal_with_message_success():
    """Testa o caso de sucesso para assert_equal_with_message."""
    assert_equal_with_message(2 + 2, 4, "Soma incorreta")


def test_assert_equal_with_message_failure():
    """Testa o caso de falha para assert_equal_with_message."""
    with pytest.raises(AssertionError) as exc_info:
        assert_equal_with_message(2 + 2, 5, "Soma incorreta")
    assert "Soma incorreta" in str(exc_info.value)
    assert "Esperado: 5" in str(exc_info.value)
    assert "Obtido: 4" in str(exc_info.value)


def test_assert_status_code_invalid_response():
    """Testa o caso de resposta inválida para assert_status_code."""
    response = object()  # Objeto sem status_code
    with pytest.raises(AssertionError) as exc_info:
        assert_status_code(response, 200)
    assert "Código de status inválido" in str(exc_info.value)


def test_assert_in_response_invalid_response():
    """Testa o caso de resposta inválida para assert_in_response."""
    response = object()  # Objeto sem text
    with pytest.raises(AssertionError) as exc_info:
        assert_in_response(response, "test")
    assert "Conteúdo 'test' não encontrado" in str(exc_info.value)


# 🏃 Para rodar os testes, execute:
# pytest tests/test_assertions.py --maxfail=1 --disable-warnings -v

if __name__ == "__main__":
    pytest.main(["-v", "tests/test_assertions.py"])
