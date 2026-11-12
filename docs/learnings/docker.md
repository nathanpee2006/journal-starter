11/10/2026

# What did I do?

Created a Dockerfile and YAML file for docker-compose to run the Journal API in a Docker container locally


# What worked?

`docker compose -f docker-compose-with-Dockerfile.yml up --build -d` runs two containers and uses a Dockerfile to build the FastAPI image. This is helpful as it automates the process of spinning up containers up and down.

A `.dockerignore` file is helpful as it excludes unneccessary files from being included in the image such as sensitive API keys.


# What I struggled with, and how did I solve it?


After using `docker build` to create the image and `docker run` to run the container, I opened http://localhost:8000 and it could not load the site.

First thing that I checked was the logs of the container.

```
docker logs journal-api
ERROR:    Error loading ASGI app. Could not import module "main".
```

Based on the error, it said that it could not find main.py which is the entrypoint of the application. The fix was to specify the directory where the main.py file was located. Instead of `main:app` it was supposed to be `api.main:app`.

Another error that I encountered was a 500 Internal Server Error.

I checked logs first of the FastAPI container and found the error message. `asyncpg.exceptions.UndefinedTableError: relation "entries" does not exist`

This told me that the DB tables were not created initially when the DB container was built. The next thing I checked was the docker compose file and realized that the .sql setup scripts where being referenced incorrectly. It was ../ but should have been ./ to indicate that docker-compose should use the current directory and not the parent. I then did `docker compose -f docker-compose-with-Dockerfile.yml down -v` and `docker compose -f your-compose-file.yaml up --build -d` to force PostgreSQL to re-initialize and execute the setup scripts. Checking the API again, the CRUD operations were now working as expeceted.

