# Dataclass Parser

Библиотека для удобного преобразования данных между Python dataclasses и другими форматами (JSON, ORM объекты и т.д.).

## Основные возможности
- Автоматически преобразует данные в/из dataclass объектов
- Поддерживает вложенные структуры данных
- Обрабатывает сложные типы (UUID, Enum, Decimal, Path, datetime)
- Поддерживает Union и Optional типы
- Работает с коллекциями (list, set, tuple, dict)
- Предотвращает рекурсивные циклы в структурах данных
- Поддержка как синхронного, так и асинхронного API

## Установка
```bash
pip install dataclass-parser
```

## Использование

### Синхронный API

```python
from dataclass_parser import EntityBase
from dataclasses import dataclass
from datetime import datetime

@dataclass
class User(EntityBase):
    id: int
    name: str
    created_at: datetime
    
# Загрузка данных
data = {"id": 1, "name": "John", "created_at": "2023-01-01T12:00:00"}
user = User.parse(data)

# Выгрузка данных
user_dict = user.serialize(exclude=['id'])  # {"name": "John", "created_at": "2023-01-01T12:00:00"}
```

### Асинхронный API

```python
from dataclass_parser.async_parser import AEntityBase
from dataclasses import dataclass
from datetime import datetime
import asyncio

@dataclass
class User(AEntityBase):
    id: int
    name: str
    created_at: datetime

async def main():
    # Загрузка данных
    data = {"id": 1, "name": "John", "created_at": "2023-01-01T12:00:00"}
    user = await User.parse(data)
    
    # Выгрузка данных
    user_dict = await user.serialize()
    
    print(user)
    print(user_dict)

if __name__ == "__main__":
    asyncio.run(main())
```

## Поддерживаемые типы данных

### Простые типы
- int, float, str, bool
- datetime, date, time
- UUID
- Decimal
- Path
- Enum

### Сложные типы
- Вложенные dataclass объекты
- Optional/Union типы (включая None)
- Коллекции:
  - list[T]
  - set[T]
  - tuple[T, ...] 
  - dict[K, V]
- Вложенные коллекции (например, list[list[int]])

## Продвинутые возможности

### Кастомная обработка типов

Библиотека позволяет расширять обработку типов данных с помощью кастомных обработчиков.

### Обработка рекурсивных структур

Библиотека автоматически обрабатывает циклические ссылки и рекурсивные структуры, предотвращая бесконечные циклы.

### Типизация

Полная поддержка аннотаций типов, что обеспечивает корректную работу статических анализаторов типов, таких как mypy.

## Примеры

Для дополнительных примеров смотрите директорию `dataclass_parser/examples/`. 

## Лицензия

MIT License

Copyright (c) 2023 EnterNick

Подробности смотрите в файле [LICENSE](LICENSE). 