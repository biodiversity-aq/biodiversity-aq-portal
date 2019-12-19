# Home app

## Structure 

```
Page
    |__ Section 
            |__ Card
            |__ Card
            |__ Card    
    |__ Section 
            |__ Card
            |__ Card
            |__ Card
```

## Dump data into fixture

```
python manage.py dumpdata home --indent 2 > home/fixtures/initial-data.json
```

## Load fixture into database

Requires `settings.FIXTURE_DIRS` to be defined. Currently defined in [biodiversity/settings/base.py](./biodiversity/settings/base.py)

```
python manage.py loaddata initial-data.json
```
