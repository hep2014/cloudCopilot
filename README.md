## CloudHackaton — Генератор API, manual и UI E2E тестов на базе Cloud.ru LLM
Проект представляет собой сервис для автоматической генерации тестов (API, manual в формате Allure TestOps as Code, UI E2E), используя Cloud.ru Foundation Models (Qwen3-Coder 480B A35B Instruct).
Сервис разворачивается полностью в Docker-контейнерах и доступен сразу после запуска.
## Установка
#### 1. Установите Docker и Docker Compose
**Для Ubuntu:**
```
sudo apt update
sudo apt install docker.io docker-compose-plugin -y
```
Проверьте, что всё установлено:
```
docker --version
docker compose version
```
#### 2. Клонирование репозитория
```
git clone https://github.com/hep2014/cloudCopilot.git
cd cloudCopilot
```
## Конфигурация окружения
Перед запуском необходимо создать файл .env в каталоге backend:
```
CLOUDRU_API_KEY=<ваше_значение>
CLOUDRU_BASE_URL=<ваше_значение>
CLOUDRU_MODEL=<ваше_значение>
CLOUDRU_KEY_ID=<ваше_значение>
CLOUDRU_KEY_SECRET=<ваше_значение>
```
#### Описание параметров:
- CLOUDRU_API_KEY	API -> token сервисного пользователя Cloud.ru
- CLOUDRU_BASE_URL	-> URL Foundation Models API
- CLOUDRU_MODEL	-> Имя вызываемой модели
- CLOUDRU_KEY_ID	-> Идентификатор API-ключа (по документации Cloud.ru)
- CLOUDRU_KEY_SECRET	-> Секретный ключ
## Запуск сервиса 
Проект разворачивается двумя контейнерами: backend (FastAPI) и frontend (Vite → Nginx).
```
docker compose build
docker compose up -d
```
После запуска:
- Backend доступен по адресу: http://localhost:8000
- Frontend доступен по адресу: http://localhost
Проверка статуса:
```
docker ps
```
Чтобы посмотреть логи backend:
```
docker logs backend
```
## API — ручки для генерации тестов 
Ниже описаны основные endpoints FastAPI. 
#### Генерация API теста
```
POST /llm/generate-api-test
```
Пример запроса: 
```
{
  "openapi": "<строка openapi.yaml>",
  "endpoint_path": "/auth/login",
  "method": "POST"
}
```
Ответ: 
```
{
  "code": "сгенерированный pytest-код",
  "validation": "результаты валидации"
}
```
#### Генерация manual теста (Allure TestOps as Code) 
```
POST /llm/manual-test
```
Пример запроса:
```
{
  "requirements": "Проверка авторизации пользователя"
}
```
#### Генерация UI E2E теста
```
POST /llm/generate-ui-e2e-test
```
Пример запроса:
```
{
  "requirements": "Проверка"
}
```
#### Массовая генерация manual тестов
```
POST /llm/bulk-manual-tests
```
Пример запроса:
```
{
  "requirements": "Тестирование кнопки «Вход»",
  "count": 10
}
```
#### Массовая генерация API тестов
```
POST /llm/bulk-api-tests
```
Пример запроса: 
```
{
  "openapi": "<JSON строки OpenAPI>",
  "endpoint_path": "/api/items",
  "method": "GET",
  "count": 5
}
```
## Архитектура проекта
```
cloudCopilot/
 ├── backend/
 │    ├── app/
 │    ├── Dockerfile
 │    ├── requirements.txt
 │    └── .env
 ├── frontend/
 │    ├── Dockerfile
 │    └── nginx.conf
 ├── docker-compose.yml
 └── tests/
```
- Backend — FastAPI
- Frontend — Vite (React) + Nginx
- Сборка — Docker Compose
