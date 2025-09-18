# Junior--Python_test_task
Выполненное тестовое задание


## Структура

```
.
├── Dockerfile
├── README.md
├── api
│   ├── answers.py
│   └── questions.py
├── config
│   ├── config.py
│   └── models.py
├── database
│   ├── __init__.py
│   ├── database.py
│   ├── database_init.py
│   └── models.py
├── docker-compose.yml
├── logs.log
├── main.py
├── migrations
│   └── env.py
├── requirements.txt
└── tests
    ├── conftest.py
    ├── test_answers_api.py
    └── test_question_api.py
```

---

## Требования

* Docker Desktop (macOS / Windows) **или** Docker Engine (Linux)
* Docker Compose v2 (`docker compose ...`)
* Bash shell

---

## Запуск

### 1) Склонировать репозиторий

```bash
git clone https://github.com/xvpaul/Junior--Python_test_task.git
```

### 2) Настроить .env

Создание `config/.env`. В корне репозитория выполнить:

```bash
mkdir -p config
cat > config/.env <<'EOF'
DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/postgres 
LOG_DIR=./
LOG_NAME=logs.log
EOF
```

### 3) Запуск

```bash
docker compose up --build
```

Перейти на:

```
http://127.0.0.1:8000
```

# Тесты

```bash
docker compose run --rm app pytest -q
```


## Остановка

```bash
docker compose down                      
```
