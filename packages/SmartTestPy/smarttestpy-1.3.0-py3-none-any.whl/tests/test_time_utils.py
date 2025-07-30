from datetime import datetime, timedelta

import pytest

from SmartTestPy.time_utils import (add_time, fixed_time, get_current_time,
                                    subtract_time)


# 🕒 Testes para get_current_time
def test_get_current_time_default():
    """✅ Testa se o tempo atual é retornado no formato padrão."""
    current_time = get_current_time()
    expected_format = "%Y-%m-%d %H:%M:%S"
    datetime.strptime(current_time, expected_format)  # Se falhar, lança ValueError  # noqa501


def test_get_current_time_custom_format():
    """🕒 Testa se o tempo atual é retornado em um formato customizado."""
    custom_format = "%d/%m/%Y"
    current_time = get_current_time(custom_format)
    datetime.strptime(current_time, custom_format)


# ⏳ Testes para add_time
def test_add_time():
    """⏳ Testa a adição de tempo ao tempo atual."""
    delta = timedelta(days=1)
    expected_time = (datetime.now() + delta).strftime("%Y-%m-%d %H:%M:%S")
    assert add_time(delta) == expected_time


def test_add_time_custom_format():
    """🕓 Testa a adição de tempo com formato customizado."""
    delta = timedelta(hours=3)
    custom_format = "%d/%m/%Y %H:%M"
    expected_time = (datetime.now() + delta).strftime(custom_format)
    assert add_time(delta, custom_format) == expected_time


# ⏳ Testes para subtract_time
def test_subtract_time():
    """⏳ Testa a subtração de tempo do tempo atual."""
    delta = timedelta(hours=1)
    expected_time = (datetime.now() - delta).strftime("%Y-%m-%d %H:%M:%S")
    assert subtract_time(delta) == expected_time


def test_subtract_time_custom_format():
    """🕓 Testa a subtração de tempo com formato customizado."""
    delta = timedelta(minutes=30)
    custom_format = "%d/%m/%Y %H:%M"
    expected_time = (datetime.now() - delta).strftime(custom_format)
    assert subtract_time(delta, custom_format) == expected_time


# 🔒 Testes para fixed_time
def test_fixed_time():
    """🔒 Testa se a função fixed_time retorna a data fixa correta."""
    expected_time = datetime(2025, 1, 1, 0, 0, 0)
    assert fixed_time() == expected_time


# 🏃 **Execução dos testes**
if __name__ == "__main__":
    pytest.main(["-v", "tests/test_time_utils.py"])
