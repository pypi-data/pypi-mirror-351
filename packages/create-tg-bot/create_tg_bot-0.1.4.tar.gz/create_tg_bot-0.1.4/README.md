# create-tg-bot

[![PyPI version](https://img.shields.io/pypi/v/create-tg-bot.svg)](https://pypi.org/project/create-tg-bot/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI/CD](https://github.com/emilastanov/create-tg-bot/actions/workflows/publish.yml/badge.svg)](https://github.com/emilastanov/create-tg-bot/actions)

📖 This README is also available in [🇷🇺 Russian](README.ru.md)

`create-tg-bot` is a Python CLI tool and boilerplate generator for creating Telegram bots using a modular and extensible architecture. It scaffolds the basic project structure, including handlers, keyboards, models, and services, and includes a `manage.py` interface for generating new components.

---

## 🔧 Features

- Modular project layout
- Jinja2 templating for generating project files
- Built-in generator for models, keyboards, and command handlers
- `manage.py` CLI powered by Click
- Templates for CRUD, keyboards, and message formatting
- Support for future integration of async ORM, logging, i18n

---

## 📦 Installation

```bash
pip install create-tg-bot
```

---

## 🚀 Quick Start

1. **Install the package:**

```bash
pip install create-tg-bot
```

2. **Generate a new bot project:**

```bash
create-tg-bot my_bot
cd my_bot
```

3. **Use CLI to generate components:**

```bash
python manage.py gen-model user
python manage.py gen-keyboard main
python manage.py gen-command start
```

---

## 📁 Project Structure

```
project/
├── .env                      # Environment variables for local development
├── alembic.ini               # Alembic configuration file for DB migrations
├── config.py                 # Global configuration settings (token, DB URL, etc.)
├── main.py                   # Entry point to start the bot
├── models/                   # SQLAlchemy models for database schema
├── services/                 # Business logic and service layer
├── crud/                     # Functions for Create, Read, Update, Delete operations
├── migrations/               # Alembic migration scripts for database versioning
├── templates/                # Jinja2 templates for code generation
├── requirements.txt          # Python dependencies
├── commands/                 # Message handlers for bot commands (e.g. /start, /help)
├── keyboards/                # Inline and reply keyboard definitions
├── button_handlers/          # Callback query handlers for inline buttons
├── texts/                    # Static texts and formatting functions
├── utils/                    # General-purpose helper functions
├── manage.py                 # CLI entry point to generate code via Click commands
└── .github/workflows/        # CI/CD pipeline definitions (e.g., GitHub Actions)

```

---

## 🧪 Development Notes

- Uses `setuptools_scm` for automatic versioning
- Templates live in `create_tg_bot/templates`
- CLI interface powered by `Click`

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 👤 Author

[Emil Astanov](mailto:emila1998@yandex.ru)
