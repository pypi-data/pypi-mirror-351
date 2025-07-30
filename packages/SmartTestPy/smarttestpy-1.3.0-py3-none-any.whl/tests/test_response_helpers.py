import pytest

from SmartTestPy.response_helpers import (assert_header, assert_json_response,
                                          assert_status_and_json)


# 🔄 Classe mock para simular respostas HTTP
class MockResponse:
    def __init__(self, status_code, json_data, headers):
        self.status_code = status_code
        self._json_data = json_data
        self.headers = headers

    def json(self):
        return self._json_data


# 🌐 ✅ Testes para assert_json_response
def test_assert_json_response_pass():
    response = MockResponse(200, {"message": "Sucesso"}, {"Content-Type": "application/json"})  # noqa501
    assert_json_response(response, {"message": "Sucesso"})


def test_assert_json_response_fail_content_type():
    response = MockResponse(200, {"message": "Sucesso"}, {"Content-Type": "text/html"})  # noqa501
    with pytest.raises(AssertionError, match="❌ Content-Type inválido"):
        assert_json_response(response, {"message": "Sucesso"})


def test_assert_json_response_fail_json():
    response = MockResponse(200, {"message": "Erro"}, {"Content-Type": "application/json"})  # noqa501
    with pytest.raises(AssertionError, match="❌ JSON incorreto"):
        assert_json_response(response, {"message": "Sucesso"})


# 🏷 ⚡ Testes para assert_header
def test_assert_header_pass():
    response = MockResponse(200, {}, {"X-Auth": "12345"})
    assert_header(response, "X-Auth", "12345")


def test_assert_header_fail():
    response = MockResponse(200, {}, {"X-Auth": "67890"})
    with pytest.raises(AssertionError, match="❌ Valor incorreto para o cabeçalho"): # noqa501
        assert_header(response, "X-Auth", "12345")


# 🔄 🌟 Testes para assert_status_and_json
def test_assert_status_and_json_pass():
    response = MockResponse(200, {"message": "OK"}, {"Content-Type": "application/json"}) # noqa501
    assert_status_and_json(response, 200, {"message": "OK"})


def test_assert_status_and_json_fail_status():
    response = MockResponse(404, {"message": "OK"}, {"Content-Type": "application/json"}) # noqa501
    with pytest.raises(AssertionError, match="❌ Código de status inválido"):
        assert_status_and_json(response, 200, {"message": "OK"})


def test_assert_status_and_json_fail_json():
    response = MockResponse(200, {"message": "Erro"}, {"Content-Type": "application/json"}) # noqa501
    with pytest.raises(AssertionError, match="❌ JSON incorreto"):
        assert_status_and_json(response, 200, {"message": "OK"})


# 🏃 **Execução dos testes**
if __name__ == "__main__":
    pytest.main(["-v", "tests/test_api.py"])
