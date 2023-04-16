- ![yamdb workflow](https://github.com/ioann7/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)
- IP проекта: 51.250.86.15
- Hostname: yatube-practicum.sytes.net
# Foodgram
Cервис для публикаций и обмена рецептами.

Авторизованные пользователи могут подписываться на понравившихся авторов, добавлять рецепты в избранное, сохранять их в список покупок и загружать список покупок. Неавторизованные пользователи могут зарегистрироваться, авторизоваться и просматривать рецепты других пользователей.

## Автор
Чимров Иоанн 47 когорта Яндекс.Практикума

## Стек технологий
- Python 3.7.7
- Django 3.2.18
- Django REST Framework 3.14
- Полный список зависимостей Python можно найти по пути `backend/requirements.txt`
- PostgreSQL 13.0
- Nginx 1.21.3
- Yandex.Cloud
- Docker
- Docker Compose

## Установка проекта на сервер
#### 1. Скопируйте файлы из папки /infra/:
```bash
scp -r infra/ <username>@<server_ip>:~/
```

#### 2. Создайте на сервере файл `.env`:
```bash
touch .env
nano .env   # Открыть для редактирования
```

Затем добавьте в него следующее содержимое:
```
DB_ENGINE=django.db.backends.postgresql
POSTGRES_DB=название_бд_на_ваш_выбор
POSTGRES_USER=имя_пользователя_для_бд_на_ваш_выбор
POSTGRES_PASSWORD=пароль_для_бд_на_ваш_выбор
DB_HOST=db
DB_PORT=5432
DJANGO_SECRET=секретный_ключ_на_ваш_выбор
```

#### 3. Отредактируйте файл конфигурации `nginx.conf` на сервере:
```bash
nano nginx.conf
```

Добавьте IP адрес вашего сервера в переменную `server_name`. Начало файла должно выглядеть следующим образом:
```
server {
    server_name <здесь_ip_адрес_вашего_сервера>;
    server_tokens off;
    listen 80;

    location /media/ {
        autoindex on;
...
```

#### 4. Убедитесь, что на сервере установлен Docker и Docker Compose.

Для установки на Ubuntu выполните следующие команды:
```bash
sudo apt update
sudo apt install docker docker-compose
```

Инструкции по установке на другие операционные системы можно найти в [документации](https://docs.docker.com/engine/install/) и [документации по установке Docker Compose](https://docs.docker.com/compose/install/).

### Настройка проекта

#### 5. Запустите сборку контейнеров на сервере командой:
```bash
sudo docker compose up -d
```

#### 6. Примените миграции:
```bash
sudo docker compose exec backend python manage.py migrate
```

#### 7. Соберите статику:
```bash
sudo docker compose exec backend python manage.py collectstatic
```

#### 8. Создайте администратора:
```bash
sudo docker compose exec backend python manage.py createsuperuser
```

#### 9. Заполните базу данных из файлов CSV (опционально):

Сначала скопируйте папку `data` на сервер:
```bash
scp -r data/ <username>@<server_ip>:~/foodgram_data/
```

Затем переместите её в контейнер backend командой:
```bash
sudo docker cp ~/foodgram_data/ <ID_контейнера_бэкенда>:/foodgram_data/

```

Теперь запустите создание объектов командой:
```bash
sudo docker compose exec backend python manage.py csv_to_db /foodgram_data/ all
```

## Установка проекта локально
Для установки проекта локально, необходимо выполнить те же самые шаги, что и для установки на сервере, за исключением того, что вместо сервера используется ваш компьютер. Кроме того, в файле конфигурации `nginx.conf` нужно указать `127.0.0.1` в переменной `server_name`.


## Документация к API
Для доступа к локальной документации необходимо запустить сервер и перейти по ссылке.
[http://127.0.0.1/api/docs/](http://127.0.0.1/api/docs/)
