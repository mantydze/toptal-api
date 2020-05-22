# Toptal Test Project. Restful API

## About

Python3 based REST API that tracks jogging times of users.

### Project requirements

- API Users must be able to create an account and log in.
- All API calls must be authenticated.
- Implement at least three roles with different permission levels: a regular user would only be able to CRUD on their owned records, a user manager would be able to CRUD only users, and an admin would be able to CRUD all records and users.
- Each time entry when entered has a date, distance, time, and location.
- Based on the provided date and location, API should connect to a weather API provider and get the weather conditions for the run, and store that with each run.
- The API must create a report on average speed & distance per week.
- The API must be able to return data in the JSON format.
- The API should provide filter capabilities for all endpoints that return a list of elements, as well should be able to support pagination.
- The API filtering should allow using parenthesis for defining operations precedence and use any combination of the available fields. The supported operations should at least include or, and, eq (equals), ne (not equals), gt (greater than), lt (lower than).
Example -> (date eq '2016-05-01') AND ((distance gt 20) OR (distance lt 10)).
- Write unit and e2e tests.

## Download and installation

Clone the repository
```
git clone git@git.toptal.com:screening/mantas-stankevicius.git
```

Setup environment and install packages
```
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Run application
```
python run.py --config_path config.json
```
Open in a browser [http://localhost:4567/](http://localhost:4567/)

### Run tests
```
coverage run tests.py --config_path testing-config.json
coverage html
```

### Run in development mode
- Make a copy of `config.json` and name it `development-config.json`
- change value of `DEBUG` to `true`
- change value of `DEBUG_TB_PROFILER_ENABLED` to `true`
- Change value of `SQLALCHEMY_DATABASE_URI` to `"sqlite:///../dev-db.sqlite"`
- Change value of `RECREATE_DATABASE` to `true`. This creates a fresh database with predefined list of users, managers and developers.

- Run `python run.py --config_path config.json`

## Endpoints

|  | endpoint | method | payload |
|------------------------------------|---------------------------|--------|-------------------------------------------------------------------------------------------------------------------------------|
| Register new user | /register | POST | {"username": "`my_name`", "password": "`my_pass`"} |
| Login user | /login | POST | {"username": "`my_name`", "password": "`my_pass`"} |
| Logout current user | /logout | GET |  |
| Info about current user | /whoami | GET |  |
| List of users | /users | GET |  |
| Create new user (same as register) | /users | POST |  |
| Update user | /users/{`user_id`} | PUT | {"username": "`my_name`", "password": "`my_pass`", "role": "`user/manager/admin`"} |
| Delete user | /users/{`user_id`} | DELETE |  |
| User report per year-week | /users/{`user_id`}/report | GET |  |
| List of runs | /runs | GET |  |
| Create new run | /runs | POST | {"user_id": `{123}`, "date": "`{2020-03-14}`", "duration": `3600`, "distance": `1000`, "latitude": `4.4`, "longitude": `3.3`} |
| Update run | /runs/{`run_id`} | PUT | {"date": "`{2020-03-14}`", "duration": `3600`, "distance": `1000`, "latitude": `4.4`, "longitude": `3.3`} |
| Delete run | /runs/{`run_id`} | DELETE |  |

## Filtering, sorting, pagination
Endpoints which return list of rows (/users, /runs) support filtering operations described below

| action | parameter | explanation |
|------------------------|--------------------------------------------------------------|------------------------------------------------------------------|
| Filtering | ?filter=(`field1` ge `1`) OR ((`field2` lt `99`) AND (`field2` ne `66`)) | (`field1` > `1`) or ((`field2` < `99`) and (`field2` != `66`)) |
| Filtering operator | eq is ==, ne is !=, lt is <, le is <=, gt is >, ge is >= | lower case only |
| Filtering conjunctions | AND, OR | UPPER CASE ONLY |
| Sorting | ?sort=`field1` | Ascending order |
|  | ?sort=`-field2` | Descending order (see dash in front) |
|  | ?sort=`field1`,`-field2` | Sort by `field1` in ASC order and then by `field2` in DESC order |
| Pagination | ?page[size]=`10` | 10 rows per page |
|  | &page[number]=`2` | second page |

