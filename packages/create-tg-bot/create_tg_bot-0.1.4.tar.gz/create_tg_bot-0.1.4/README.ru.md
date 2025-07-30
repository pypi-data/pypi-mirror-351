# create-tg-bot

[![PyPI version](https://img.shields.io/pypi/v/create-tg-bot.svg)](https://pypi.org/project/create-tg-bot/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI/CD](https://github.com/emilastanov/create-tg-bot/actions/workflows/publish.yml/badge.svg)](https://github.com/emilastanov/create-tg-bot/actions)

📖 Этот README также доступен на [🇬🇧 английском](README.md)

`create-tg-bot` — это CLI-инструмент на Python и генератор шаблонов для создания Telegram-ботов с модульной и расширяемой архитектурой. Он создает базовую структуру проекта, включая обработчики, клавиатуры, модели и сервисы, и предоставляет интерфейс `manage.py` для генерации новых компонентов.

---

## 🔧 Возможности

- Модульная структура проекта
- Jinja2-шаблоны для генерации файлов проекта
- Встроенный генератор моделей, клавиатур и обработчиков команд
- CLI-интерфейс `manage.py` на базе Click
- Шаблоны для CRUD, клавиатур и форматирования сообщений
- Поддержка будущей интеграции асинхронного ORM, логирования и i18n

---

## 📦 Установка

```bash
pip install create-tg-bot
```

---

## 🚀 Быстрый старт

1. **Установите пакет:**

```bash
pip install create-tg-bot
```

2. **Создайте новый проект бота:**

```bash
create-tg-bot my_bot
cd my_bot
```

3. **Используйте CLI для генерации компонентов:**

```bash
python manage.py gen-model user
python manage.py gen-keyboard main
python manage.py gen-command start
```

---

## 📁 Структура проекта

```
project/
├── .env                      # Переменные окружения для локальной разработки
├── alembic.ini               # Конфигурационный файл Alembic для миграций
├── config.py                 # Глобальные настройки (токен, адрес БД и т.д.)
├── main.py                   # Точка входа для запуска бота
├── models/                   # Модели SQLAlchemy для описания схемы БД
├── services/                 # Бизнес-логика и сервисный слой
├── crud/                     # Функции для операций Create, Read, Update, Delete
├── migrations/               # Скрипты миграций Alembic
├── templates/                # Jinja2-шаблоны для генерации кода
├── requirements.txt          # Зависимости Python
├── commands/                 # Обработчики команд (например, /start, /help)
├── keyboards/                # Описание inline и reply-клавиатур
├── button_handlers/          # Обработчики нажатий на inline-кнопки
├── texts/                    # Статичные тексты и функции форматирования
├── utils/                    # Вспомогательные утилиты
├── manage.py                 # CLI-интерфейс для генерации кода через Click
└── .github/workflows/        # Конфигурация CI/CD (например, GitHub Actions)

```

---

## 🧪 Заметки по разработке

- Используется `setuptools_scm` для автоматического версионирования
- Шаблоны расположены в `create_tg_bot/templates`
- CLI-интерфейс построен на `Click`

---

## 📄 Лицензия

Этот проект распространяется под лицензией [MIT License](LICENSE).

---

## 👤 Автор

[Emil Astanov](mailto:emila1998@yandex.ru)
