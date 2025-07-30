# 📦 smarttestpy/time_utils.py

from datetime import datetime, timedelta

from freezegun import freeze_time


def get_current_time(format_str="%Y-%m-%d %H:%M:%S"):
    """
    🕒 Retorna o tempo atual no formato especificado.

    Args:
        format_str (str): Formato da data/hora a ser retornada.

    Returns:
        str: Data/hora formatada.
    """
    return datetime.now().strftime(format_str)


def add_time(delta: timedelta, format_str="%Y-%m-%d %H:%M:%S"):
    """
    ⏳ Adiciona um intervalo de tempo ao tempo atual e retorna o valor formatado. # noqa501

    Args:
        delta (timedelta): Intervalo de tempo a ser adicionado.
        format_str (str): Formato da data/hora retornada.

    Returns:
        str: Data/hora resultante formatada.
    """
    new_time = datetime.now() + delta
    return new_time.strftime(format_str)


def subtract_time(delta: timedelta, format_str="%Y-%m-%d %H:%M:%S"):
    """
    ⏳ Subtrai um intervalo de tempo do tempo atual e retorna o valor formatado.

    Args:
        delta (timedelta): Intervalo de tempo a ser subtraído.
        format_str (str): Formato da data/hora retornada.

    Returns:
        str: Data/hora resultante formatada.
    """
    new_time = datetime.now() - delta
    return new_time.strftime(format_str)


@freeze_time("2025-01-01 00:00:00")
def fixed_time():
    """
    🔒 Retorna uma data fixa usando freezegun para testes.

    Returns:
        datetime: Data fixa (2025-01-01 00:00:00).
    """
    return datetime.now()


# 🌟 Exemplo de uso
if __name__ == "__main__":
    print("🕒 Tempo atual:", get_current_time())
    print("⏳ +1 dia:", add_time(timedelta(days=1)))
    print("⏳ -1 hora:", subtract_time(timedelta(hours=1)))
    print("🔒 Tempo fixo:", fixed_time())
