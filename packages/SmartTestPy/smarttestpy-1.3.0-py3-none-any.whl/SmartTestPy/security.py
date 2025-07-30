import requests
import jwt
from typing import Dict, List, Union, Optional
import re

class SecurityScanner:
    def __init__(self):
        self.common_vulnerabilities = [
            "XSS",
            "CSRF",
            "SQL Injection",
            "Command Injection",
            "File Inclusion"
        ]

    def scan(self, url: str) -> Dict:
        """
        Performs a basic security scan of the given URL.
        
        Args:
            url (str): The URL to scan
            
        Returns:
            Dict: Dictionary containing scan results
        """
        try:
            response = requests.get(url)
            vulnerabilities = []
            
            # Check for common security headers
            if "X-Frame-Options" not in response.headers:
                vulnerabilities.append("Missing X-Frame-Options header")
            if "X-Content-Type-Options" not in response.headers:
                vulnerabilities.append("Missing X-Content-Type-Options header")
            if "Strict-Transport-Security" not in response.headers:
                vulnerabilities.append("Missing HSTS header")
                
            return {
                "vulnerabilities": vulnerabilities,
                "status_code": response.status_code,
                "headers": dict(response.headers)
            }
        except Exception as e:
            return {
                "vulnerabilities": ["Error during scan: " + str(e)],
                "status_code": None,
                "headers": {}
            }

class SQLInjectionTester:
    def __init__(self):
        self.common_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users; --"
        ]

    def test_injection(self, url: str, payload: str) -> bool:
        """
        Tests for SQL injection vulnerability using the provided payload.
        
        Args:
            url (str): The URL to test
            payload (str): The SQL injection payload to test
            
        Returns:
            bool: True if potential vulnerability detected, False otherwise
        """
        try:
            response = requests.post(url, data={"input": payload})
            
            # Check for common SQL error messages
            error_patterns = [
                "SQL syntax",
                "mysql_fetch_array",
                "ORA-",
                "PostgreSQL",
                "SQLite"
            ]
            
            for pattern in error_patterns:
                if pattern.lower() in response.text.lower():
                    return True
                    
            return False
        except Exception:
            return False

class SecurityHeadersValidator:
    def __init__(self):
        self.required_headers = {
            "X-Frame-Options": ["DENY", "SAMEORIGIN"],
            "X-Content-Type-Options": ["nosniff"],
            "Strict-Transport-Security": [r"max-age=\d+"],
            "Content-Security-Policy": [r".*"],
            "X-XSS-Protection": ["1", "1; mode=block"]
        }

    def validate_headers(self, headers: Dict[str, str]) -> Dict:
        """
        Validates security headers against best practices.
        
        Args:
            headers (Dict[str, str]): Dictionary of headers to validate
            
        Returns:
            Dict: Dictionary containing validation results
        """
        missing_headers = []
        invalid_values = []
        
        for header, valid_values in self.required_headers.items():
            if header not in headers:
                missing_headers.append(header)
            else:
                value = headers[header]
                is_valid = False
                for valid_value in valid_values:
                    if re.match(valid_value, value):
                        is_valid = True
                        break
                if not is_valid:
                    invalid_values.append(f"{header}: {value}")
                    
        return {
            "missing_headers": missing_headers,
            "invalid_values": invalid_values,
            "is_secure": len(missing_headers) == 0 and len(invalid_values) == 0
        }

class JWTChecker:
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or "your-secret-key"

    def validate_token(self, token: str) -> Dict:
        """
        Validates a JWT token.
        
        Args:
            token (str): The JWT token to validate
            
        Returns:
            Dict: Dictionary containing validation results
        """
        try:
            # Decode the token
            decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            
            # Check for required claims
            required_claims = ["exp", "iat"]
            missing_claims = [claim for claim in required_claims if claim not in decoded]
            
            return {
                "is_valid": True,
                "decoded": decoded,
                "missing_claims": missing_claims
            }
        except jwt.ExpiredSignatureError:
            return {
                "is_valid": False,
                "error": "Token has expired"
            }
        except jwt.InvalidTokenError as e:
            return {
                "is_valid": False,
                "error": str(e)
            } 