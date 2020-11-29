This is a dev environment with Browsable API and Local Database

# To run for the first time (in root folder)

docker-compose build

docker-compose run app sh -c "python manage.py makemigrations"

docker-compose up

# To run tests

docker-compose run --rm app sh -c "python manage.py test && flake8"

# To run app (*not for the first time)

docker-compose up
