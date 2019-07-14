Шаги по создание БД
---

Ссыль на источник:

https://tutorial-extensions.djangogirls.org/en/optional_postgresql_installation/

Кратко:
* Запустить **psql**

* Создать пользователя

    ```
    # CREATE USER <name>;
    ```

* Создать БД

    ```
    # CREATE DATABASE <db_name> OWNER <name>;
    ```

* Обновить настрйоки преокта типа
    ```
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': '<db_name>',
            'USER': '<name>',
            'PASSWORD': '<pswrd>',
            'HOST': 'localhost',
            'PORT': '',
        }
    }
    ```
* Подготовить миграции

        python manage.py makemigrations

* Применить миграции

        python manage.py migrate
