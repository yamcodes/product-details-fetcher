# product-details-fetcher

## Prerequisites
This project uses sqlite3, to simplify the development of an SQL database. In production, it is recommended to switch to PostgreSQL or MySQL. To run this project, please make sure you have sqlite3 installed. If you have a macOS, it is installed by default.
## Install & Run
1. Run `virtualenv venv` (or `python -m virtualenv venv`)
2. On Linux/macOS, `source  venv/bin/activate`, on Windows, `venv/bin/activiate`
3. Install dependencies with `pip install -r requirements.txt`
4. Run the server with `sanic server.app` (or `python -m sanic server.app`)

You may use a program such as Postman or Insomnia to access the endpoints, which are:

`localhost:8000/details GET`

`localhost:8000/details/<source:(amazon|walmart)>/<source_id:str> GET`

`localhost:8000/details/<source:(amazon|walmart)>/<source_id:str> PUT`

`localhost:8000/favorites/<source_id:str> PUT`
