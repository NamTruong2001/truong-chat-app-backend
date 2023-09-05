# Truong chat application


## Prerequisites
- Python >= 3.9
- MySQL

## Getting started

- In the project directory, run the command below to install the dependencies
```
pip install -r requirements.txt
```
- Config your database information in *app/db/database* and *alembic.ini* file
- Run this command to setup mysql database
```
alembic upgrade head
```
- Run the command below to start the project

```
uvicorn main:app --host 0.0.0.0 --port 8000 
```