# biodiversity-aq

Django app for SCAR Antarctic Biodiversity Portal ([www.biodiversity.aq](http://www.biodiversity.aq)).

Pre-installed apps:
- accounts (authentication)
- POLA3R (formerly MARS) 

The data app will eventually be installed in this project.  

## Installation (local development)

### Setup database

1. Create an empty PostgreSQL database (e.g. biodiversityaq)
2. Enable PostGIS: `CREATE EXTENSION postgis;`

### Define settings

1. Clone this repository: `git clone https://git.bebif.be/antabif/biodiversityaq.git`
2. Create a local settings file in settings directory: `touch biodiversity/settings/local.py`
3. In that file, include the following settings: 

Override `{{ my user }}` and  `{{ my password }}`.

```python
DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': 'biodiversity_aq',
            'USER': '{{ my user }}',
            'PASSWORD': '{{ my password }}',
            'HOST': '',
            'PORT': '5432'
        }
    }

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

```

### Setup python environment

In your terminal, run the following commands:

1. Create a virtual environment, e.g. `conda create -n biodiversityaq python=3.7`
2. Activate the environment, e.g. `source activate biodiversityaq`
3. Navigate to the project directory and install the requirements: `pip install -r requirements-dev.txt`

### Apply database migrations

Database migrations create tables from Django models into the database. To do so, run the following commands in your 
terminal:

```
python manage.py migrate
```

### Create superuser

In your terminal, run:

```
python manage.py createsuperuser
```

This will prompt for a username, email and password.

### Run the application

At the moment, the settings to run the application is already mentioned in `manage.py` file to use the `dev` settings. 
In your terminal, run: 

```
python manage.py runserver
```

Open a browser and go to [http://localhost:8000](http://localhost:8000) to view the application.
