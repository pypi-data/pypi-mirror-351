# FunpayAce

[![PyPI version](https://badge.fury.io/py/funpayace.svg)](https://pypi.org/project/funpayace/)

Библиотека для продавцов Funpay, позваляющая удобно управлять аккаунтом, а так же получать статистику.

---

## 🚀 Установка

```bash
pip install funpayace
```

---

## 🔧 Пример использования

```python
from funpayace import FunpayAce
import time

funpay = FunpayAce(golden_key="ваш_ключ")
funpay.forever_online()

# Ваш основной код или просто бесконечный цикл, чтобы не завершалась программа:
while True:
    time.sleep(1)
```

---

## ⚙️ Аргументы

```python
FunpayAce(golden_key: str)
```

- `golden_key` — cookie ключ сессии Funpay. Можно получить из браузера в инструменте разработчика (DevTools).

---

## 📒 Обновления

### v0.0.3 — 2025-05-29

- Добавлен README.md для PyPI

### v0.0.2 — 2025-05-29

- Добавлена асинхронная реализация с фоновым запуском через поток
- Улучшено логирование и обработка ошибок
- Улучшена совместимость с PyPI

### v0.0.1 — 2025-05-29

- Пустая библиотека

---

## 📜 Лицензия

Проект распространяется под лицензией MIT. См. файл [LICENSE](./LICENSE).

---

## ☕ Поддержка

Если библиотека оказалась полезной — звезда на GitHub всегда приветствуется ⭐

Телеграм-канал библиотеки: https://t.me/funpayace
