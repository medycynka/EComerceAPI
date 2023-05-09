# E-commerce API project with simple UI using 
[![python: 3.6 | 3.7 | 3.8 | 3.9](https://img.shields.io/badge/python-3.6_%7c_3.7_%7c_3.8_%7c_3.9-%23007ec6)](https://www.python.org/)
[![Django: 4.2](https://img.shields.io/badge/django-4.2-%2344B78B)](https://www.djangoproject.com/)
[![DRF: 3.14.0](https://img.shields.io/badge/DRF-3.14.0-%23A30000)](https://www.django-rest-framework.org/) 
[![graphene: 3.2.2](https://img.shields.io/badge/graphene-3.2.2-%23f67049)](https://graphene-python.org/) 
[![bootstrap: 5.3](https://img.shields.io/badge/bootstrap-5.3-%23712cf9)](https://getbootstrap.com/)

# Author: Szymon Peszek

## Installation / Setup instruction
The application requires the following installations to operate:
- pip
- django
- pillow
- django-cors-headers
- psycopg2-binary
- requests
- pathlib
- pyproj
- django-filter
- djangorestframework
- graphene
- graphene-django
- factory-boy
- Faker

## Technologies Used
- python 3.9.6

## Project Setup Instructions
1) git clone the repository 
```shell
gti clone https://github.com/medycynka/EComerceAPI.git
```
2. cd into EComerceAPI
```shell
cd EComerceAPI
```
3. create a virtual env
```shell
py -m venv env
```
4. activate env
```shell
env\scripts\activate
```
5. Open CMD & Install Dependencies
```shell
pip install -r requirements.txt
```
6. Make Migrations
```shell
py manage.py makemigrations
```
7. Migrate DB
```shell
py manage.py migrate
```
8. Create custom groups
```shell
py manage.py create_custom_groups
```
10. Run Application
```shell
py manage.py runserver
```

Optionally:
1. Create user with admin privileges:
```shell
py manage.py createsuperuser
```
2. Fill db with random test data (see `py manage.py fake_db_fill --help` for more info)
```shell
py manage.py fake_db_fill
```

### Project structure
1. API - models declaration, serializers, filters and rest endpoints using [![DRF: 3.14.0](https://img.shields.io/badge/DRF-3.14.0-%23A30000)](https://www.django-rest-framework.org/)
2. GraphQL - app using [![graphene: 3.2.2](https://img.shields.io/badge/graphene-3.2.2-%23f67049)](https://graphene-python.org/) 
an alternative to REST and ad-hoc webservice architectures allowing you to select which data you want to download 
instead of whole serialized object
3. UserInterface - User Interface templates and views declarations showing the possibilities of the created api 
(without using default django functionalities like _ListView_)

© 2023 Szymon Peszek

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)