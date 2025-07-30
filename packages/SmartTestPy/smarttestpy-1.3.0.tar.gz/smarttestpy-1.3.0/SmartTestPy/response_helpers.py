from requests import Response


def assert_json_response(response: Response, expected_json: dict):
    """
    🌐 ✅ Valida se a resposta JSON corresponde ao dicionário esperado.

    Args:
        response (Response): Objeto de resposta da biblioteca requests.
        expected_json (dict): Dicionário esperado na resposta.

    Raises:
        AssertionError: Se o JSON retornado não corresponder ao esperado.
    """
    assert "application/json" in response.headers.get("Content-Type", ""), (
        "❌ Content-Type inválido. Esperado 'application/json'."
    )
    assert response.json() == expected_json, (
        f"❌ JSON incorreto. Esperado: {expected_json}, Obtido: {response.json()}" # noqa501
    )


def assert_header(response: Response, header: str, value: str):
    """
    🏷 ⚡ Valida se um cabeçalho específico possui o valor esperado.

    Args:
        response (Response): Objeto de resposta.
        header (str): Nome do cabeçalho a ser verificado.
        value (str): Valor esperado do cabeçalho.

    Raises:
        AssertionError: Se o cabeçalho ou valor estiver incorreto.
    """
    actual_value = response.headers.get(header)
    assert actual_value == value, (
        f"❌ Valor incorreto para o cabeçalho '{header}'. Esperado: '{value}', Obtido: '{actual_value}'." # noqa501
    )


def assert_status_and_json(response: Response, status_code: int, expected_json: dict): # noqa501
    """
    🔄 🌟 Valida o código de status e o conteúdo JSON em uma única chamada.

    Args:
        response (Response): Objeto de resposta.
        status_code (int): Código de status esperado.
        expected_json (dict): Dicionário esperado na resposta JSON.

    Raises:
        AssertionError: Se qualquer validação falhar.
    """
    assert response.status_code == status_code, (
        f"❌ Código de status inválido. Esperado: {status_code}, Obtido: {response.status_code}." # noqa501
    )
    assert_json_response(response, expected_json)


# 🌟 Exemplo de uso
if __name__ == "__main__":
    class MockResponse:
        def __init__(self, status_code, json_data, headers):
            self.status_code = status_code
            self._json_data = json_data
            self.headers = headers

        def json(self):
            return self._json_data

    # Exemplo de resposta mockada
    mock_resp = MockResponse(
        200,
        {"message": "Sucesso"},
        {"Content-Type": "application/json"}
    )

    assert_status_and_json(mock_resp, 200, {"message": "Sucesso"})
    assert_header(mock_resp, "Content-Type", "application/json")

    print("✅ Todos os testes de API passaram!")
