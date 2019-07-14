release: python manage.py makemigrations stats && python manage.py makemigrations && python manage.py migrate && python manage.py migrate stats
web: gunicorn mysite.wsgi --log-file -