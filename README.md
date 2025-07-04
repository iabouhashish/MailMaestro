# My Email Bot 🤖📧

[![CI Status](https://github.com/your-org/my-email-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/my-email-bot/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/codecov/c/github/your-org/my-email-bot/main)](https://codecov.io/gh/your-org/my-email-bot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Automate email classification (recruiter, concert, transactional), extract key details, schedule reminders, and draft summaries—fully extensible via plugins and multi‑locale.

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/your-org/my-email-bot.git
cd my-email-bot

# Install
git checkout main
cp .env.example .env
# Fill .env with your secrets
pip install -r requirements.txt

# Run
python main.py
````

## 🧩 Plugins & Extensions

Drop new workflows into `plugins/` with `@task` decorator. Manage sequences via `pipeline.yml`.

## 🌐 Internationalization

Templates live under `prompts/${TEMPLATE_VERSION}/{en,fr,...}/`. Set `TEMPLATE_VERSION=v1` in your `.env`.

## 📚 Documentation

See [`docs/`](docs/) for architecture diagrams and API reference.

## 🤝 Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) and our [Code of Conduct](CODE_OF_CONDUCT.md).

## 📝 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
