import pytest
from SmartTestPy.security import (
    SecurityScanner,
    SQLInjectionTester,
    SecurityHeadersValidator,
    JWTChecker
)

class TestSecurityScanner:
    def test_basic_vulnerability_scan(self):
        scanner = SecurityScanner()
        result = scanner.scan("http://example.com")
        assert result is not None
        assert isinstance(result, dict)
        assert "vulnerabilities" in result

class TestSQLInjectionTester:
    def test_sql_injection_detection(self):
        tester = SQLInjectionTester()
        payload = "' OR '1'='1"
        result = tester.test_injection("http://example.com/login", payload)
        assert result is not None
        assert isinstance(result, bool)

class TestSecurityHeadersValidator:
    def test_security_headers(self):
        validator = SecurityHeadersValidator()
        headers = {
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "Strict-Transport-Security": "max-age=31536000"
        }
        result = validator.validate_headers(headers)
        assert result is not None
        assert isinstance(result, dict)
        assert "missing_headers" in result

class TestJWTChecker:
    def test_jwt_validation(self):
        checker = JWTChecker()
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        result = checker.validate_token(token)
        assert result is not None
        assert isinstance(result, dict)
        assert "is_valid" in result 