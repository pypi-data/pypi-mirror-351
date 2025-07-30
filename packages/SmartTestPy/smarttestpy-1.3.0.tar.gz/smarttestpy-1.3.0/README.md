# 📚 **SmartTestPy** - Framework Inteligente para Testes em Python

**SmartTestPy** é um pacote robusto e flexível para a criação de testes automatizados em Python. Com suporte ao `pytest`, `unittest`, geração de dados fake, mocks avançados e integração com APIs e bancos de dados, ele foi projetado para simplificar o processo de testes, desde o básico até casos avançados.

---

## ✨ **Funcionalidades Principais**
- ✅ **Assertions personalizadas** para validações detalhadas.
- 🏷 **Fixtures reutilizáveis** para cenários complexos.
- 🎭 **Mocks inteligentes** para testes isolados.
- 🌐 **Testes de API** com validação de payloads, headers e status.
- 🏦 **Gerenciamento de banco de dados** para testes integrados.
- ⏳ **Manipulação de tempo** com suporte ao `freezegun`.
- 📊 **Cobertura de código** com relatórios automatizados.
- ⚡ **Execução paralela de testes** para maior performance.
- 🛠 **Compatível com frameworks** como Django, Flask e FastAPI.
- 🌍 **Internacionalização (i18n)** para mensagens e logs de testes.

---

## ⚡ **Instalação**

Instale o **SmartTestPy** diretamente do PyPI:

```bash
pip install SmartTestPy
```

> 💡 Requisitos: Python 3.6 ou superior.

---

## 🚀 **Como Usar**  

### ✅ **Assertions Customizadas**  

```python
from SmartTestPy.assertions import assert_status_code

class MockResponse:
    def __init__(self, status_code, text=""):
        self.status_code = status_code
        self.text = text

response = MockResponse(200, "OK")
assert_status_code(response, 200)
```

---

### 🧪 **Fixtures e Mocks**  

```python
from SmartTestPy.fixtures import fake_user

user = fake_user()
assert user['email'] is not None
```

---

### 🌐 **Testes de API**  

```python
from SmartTestPy.response_helpers import assert_json_response
from requests import Session  # Importação corrigida

client = Session()  # Criando um cliente para chamadas HTTP

response = client.get("https://api.example.com/user/1/")
assert_json_response(response, {"id": 1, "name": "John Doe"})
```

---

### ⏳ **Manipulação de Tempo**  

```python
from SmartTestPy.time_utils import fixed_time

assert fixed_time().strftime("%Y-%m-%d") == "2025-01-01"
```

---

## 🏃 **Executando os Testes**  

```bash
pytest tests/ --maxfail=1 --disable-warnings -v
```

📈 **Gerar relatório de cobertura:**  

```bash
pytest --cov=SmartTestPy --cov-report=html
```

---


### 1. Testando uma API REST com validação de status e conteúdo
```python
from SmartTestPy.assertions import assert_status_code, assert_in_response
import requests

def test_api_user_creation():
    response = requests.post("https://api.exemplo.com/users", json={"name": "Ana"})
    assert_status_code(response, 201)
    assert_in_response(response, "Usuário criado com sucesso")
```

### 2. Utilizando fixtures para gerar dados dinâmicos em massa
```python
def test_register_multiple_users(fake_user):
    users = [fake_user for _ in range(5)]
    for user in users:
        assert "@" in user["email"]
```

### 3. Mockando respostas HTTP para testes isolados
```python
def test_service_with_mock_response(mock_response_200):
    response = mock_response_200
    assert response.status_code == 200
    assert response.text == "OK"
```

### 4. Manipulando o tempo em testes
```python
from SmartTestPy.time_utils import fixed_time

def test_fixed_time():
    assert fixed_time().strftime("%Y-%m-%d") == "2025-01-01"
```

### 5. Integração com pytest e relatórios de cobertura
```bash
pytest tests/ --cov=SmartTestPy --cov-report=term-missing
```

### 6. Testando unicidade e geração de dados únicos
```python
def test_unique_fake_users(fake_user):
    user1 = fake_user
    user2 = fake_user  # pytest chama a fixture novamente
    assert user1 != user2
```

### 7. Testes de Segurança
```python
from SmartTestPy.security import SecurityScanner, SQLInjectionTester, SecurityHeadersValidator, JWTChecker

# Scanner de vulnerabilidades básicas
scanner = SecurityScanner()
result = scanner.scan("https://api.exemplo.com")
print(f"Vulnerabilidades encontradas: {result['vulnerabilities']}")

# Teste de injeção SQL
tester = SQLInjectionTester()
is_vulnerable = tester.test_injection("https://api.exemplo.com/login", "' OR '1'='1")
print(f"Vulnerável a SQL Injection: {is_vulnerable}")

# Validação de headers de segurança
validator = SecurityHeadersValidator()
headers = {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Strict-Transport-Security": "max-age=31536000"
}
result = validator.validate_headers(headers)
print(f"Headers ausentes: {result['missing_headers']}")

# Validação de token JWT
checker = JWTChecker(secret_key="sua-chave-secreta")
token = "seu-token-jwt"
result = checker.validate_token(token)
print(f"Token válido: {result['is_valid']}")
```

### 8. Testes de Segurança Avançados
```python
from SmartTestPy.security import SecurityScanner

# Scanner completo de segurança
scanner = SecurityScanner()
result = scanner.scan("https://api.exemplo.com")

# Verificando headers de segurança
if "X-Frame-Options" not in result["headers"]:
    print("⚠️ Falta header X-Frame-Options")

# Verificando status da resposta
if result["status_code"] == 200:
    print("✅ Endpoint acessível")

# Verificando vulnerabilidades
for vuln in result["vulnerabilities"]:
    print(f"⚠️ {vuln}")
```

---

## 🏰 **Estrutura do Projeto**
```
SmartTestPy/
│
├── SmartTestPy/                # 📞 Código do pacote
│   ├── __init__.py
│   ├── assertions.py           # ✅ Assertions personalizadas
│   ├── fixtures.py             # 🏷 Fixtures e mocks reutilizáveis
│   ├── response_helpers.py     # 🌐 Testes e validações de APIs
│   ├── time_utils.py           # ⏳ Manipulação de tempo
│
├── tests/                      # 🧪 Testes unitários
│   ├── test_assertions.py
│   ├── test_fixtures.py
│   ├── test_response_helpers.py
│   └── test_time_utils.py
│
├── setup.py                    # ⚙️ Configuração do pacote
├── pyproject.toml              # 📚 Configuração moderna
├── README.md                   # 📚 Documentação do projeto
├── LICENSE                     # 🌍 Licença MIT
└── MANIFEST.in                 # 🗉 Inclusão de arquivos extras
```

---

## 🌐 **Compatibilidade**
- ✅ Python 3.6+
- 🚀 Compatível com **Django**, **Flask** e **FastAPI**.
- 🐍 Suporte a `pytest`, `unittest` e execução paralela com `pytest-xdist`.

---

## 📝 **Licença**

Distribuído sob a **Licença MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👨‍💻 **Autor**

Desenvolvido por **[Roberto Lima](https://github.com/robertolima-dev)** 🚀✨

---

## 💬 **Contato**

- 📧 **Email**: robertolima.izphera@gmail.com
- 💼 **LinkedIn**: [Roberto Lima](https://www.linkedin.com/in/roberto-lima-01/)
- 💼 **Website**: [Roberto Lima](https://robertolima-developer.vercel.app/)
- 💼 **Gravatar**: [Roberto Lima](https://gravatar.com/deliciouslyautomaticf57dc92af0)
---

## ⭐ **Gostou do projeto?**

Deixe uma ⭐ no repositório e compartilhe com a comunidade! 🚀✨  

```bash
git clone https://github.com/robertolima-dev/SmartTestPy.git
cd SmartTestPy
pip install -e .
```

---

## 🌟 **O que este README oferece?**
- 🎯 **Descrição clara** do projeto e seu propósito.  
- 🛠 **Instruções detalhadas de instalação** e **uso prático**.  
- 🧪 **Guia de testes** para garantir que o código funciona.  
- 🏰 **Estrutura do projeto** para facilitar a navegação.  
- 🔄 **Seção de contribuição** para quem deseja ajudar no desenvolvimento.  
- 📝 **Licença e informações do autor** para transparência.
