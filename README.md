# RedisCache

To start api use pip to install everything in requirements.txt

`pip install -r requirements.txt`

Next go to backend `cd backend` and run `uvicorn main:app --reload`

The api is now running and you should be able to test it on `http://127.0.0.1:8000/`

Make sure that neo4j database and redis database is running and you might need to change user and password for neo4j driver in main.py
