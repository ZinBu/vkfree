Выполняя __makemigrations__, вы говорите Django, что внесли некоторые изменения
в ваши модели (в нашем случае мы создали несколько новых)
и хотели бы сохранить их в миграции.
Миграции используются Django для сохранения изменений ваших моделей
(и структуры базы данных) - это просто файлы на диске.

    python manage.py makemigrations stats

В Django есть команда, которая выполняет миграции и автоматически обновляет
базу данных - она называется __migrate__.

    python manage.py migrate

---
Миграции - очень мощная штука. Они позволяют изменять ваши модели в 
процессе развития проекта без необходимости пересоздавать таблицы в базе данных.
Их задача изменять базу данных без потери данных. Мы ещё вернемся к ним,
а пока запомните эти инструкции по изменению моделей:
Внесите изменения в модели (в models.py).

- Выполните python manage.py makemigrations чтобы создать миграцию для ваших изменений

- Выполните python manage.py migrate чтобы применить изменения к базе данных.

Две команды необходимы для того, чтобы хранить миграции в системе контроля версий. 
Они не только помогают вам, но и могут использоваться другими программистами вашего проекта.