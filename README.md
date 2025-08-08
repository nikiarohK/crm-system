# CRM система

1. Убедитесь, что у тебя установлен Python 3.7 или новее
2. Установите PostgreSQL 

## Как запустить проект

1. Сначала создай виртуальное окружение и активируй его:

```bash
python -m venv venv
source venv/bin/activate  

venv\Scripts\activate  
```

2. Установи зависимости:

```bash
pip install -r requirements.txt
```

3. Создай файл `.env` в папке `api_gateway` с таким содержанием:

```
JWT_SECRET_KEY=secret_key
```

4. Запусти сервисы в разных окнах терминала:

```bash

cd customer_service
python customer_server.py


cd order_service
python order_server.py


cd api_gateway
uvicorn main:app --reload
```

1. Открой в браузере: http://localhost:8000
2. Попробуй зарегистрироваться:

- Логин: test
- Пароль: test123

## Примеры запросов 

1. Регистрация:

```
POST http://localhost:8000/register
Body (JSON):
{
  "username": "test",
  "password": "test123"
}
```

2. Вход (получим токен):

```
POST http://localhost:8000/login
Body (JSON):
{
  "username": "test",
  "password": "test123"
}
```

3. Создать клиента

```
POST http://localhost:8000/customers
Headers:
Authorization: Bearer <ваш_токен>
Body (JSON):
{
  "name": "Test Client",
  "email": "test@test.com"
}
```


## Документация

После запуска открой: http://localhost:8000/docs
