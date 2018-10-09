# flask_api

To setup and run the api server, do the following steps:

1. Run `docker-compose up`
2. Open a new terminal window and connect to the running container: `docker exec -it flask_api sh`
3. Upgrade migrations: `python manage.py db upgrade`
4. Create an admin user: `python manage.py users create_admin --email=user@example.com --password=password`

In order to update or add python packages, connect to the running container and do the following steps:

1. Install new package: `pip install package_name`
2. Update the requirements file: `docker exec flask_api pip freeze > requirements.txt`
3. Stop the flask_api container: `docker stop flask_api` or just stop previously run docker-compose
4. Rebuild the flask_api image: `docker build -t flask_api .`
5. Run docker-compose again

If you need to do any database migrations, connect to the running container and do the following steps:

1. Generate migrations: `python manage.py db migrate`
2. Review your new migration under directory: ./migrations
3. Upgrade migrations: `python manage.py db upgrade`
