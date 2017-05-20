# Destiny

Destiny is an ETL allowing to build local database from [League of Legends](http://na.leagueoflegends.com/) API. It provides a simple way to get collection of players, matches and various statistics from LoL matches through an API. Then you can easily explore data in SQL or build an interface to ask the database freshly created.

## Requierements

- Python 2.7
- Running mysql server available with a ready to use database (default name is 'lol')
- Install modules from `requierements.txt`

## Configuration

Rename `config.example.yml` to `config.yml` then change the relevant fields.


## Project Architecture

```
Destiny/
| -- destiny/
|    |
|    | -- main/
|    |    | -- bdd/
|    |    |    |-- __init__.py
|    |    |    |-- connexion.py
|    |    |    |-- models/
|    |    |    |   | -- __init__.py
|    |    |    |   | -- assistevent.py
|    |    |    |   | -- itemevent.py
|    |    |    |   | -- killevent.py
|    |    |    |   | -- matches.py
|    |    |    |   | -- participant.py
|    |    |    |   | -- player.py
|    |    |    |   | -- stats
|    |    |
|    |    | -- __init__.py
|    |    | -- __api_call.py
|    |    | -- etl/
|    |    |    |-- __init__.py
|    |    |    |-- extract.py
|    |    |    |-- load.py
|    |    |    |-- transform.py
|    |
|    | -- test/
|    |    | -- test_etl
|    |
|    | -- __init__.py
|    | -- settings.py
|    | -- utils.py
|
| -- .gitattributes
| -- .gitignore
| -- config.yaml
| -- config.yaml.example
| -- destiny.py
| -- LICENSE
| -- README.md
| -- requirements.txt
```

## License

Destiny is under MIT License.