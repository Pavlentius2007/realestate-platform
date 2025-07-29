try:
    # Переэкспортируем все публичные объекты из backend.database
    from backend.database import *  # noqa: F401,F403
except ImportError as e:
    # Если backend.database недоступен, выводим понятную ошибку
    raise ImportError(
        "Не удалось импортировать backend.database. Убедитесь, что каталог 'backend' находится в PYTHONPATH."
    ) from e 