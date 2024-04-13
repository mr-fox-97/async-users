# Async User Management System with python

This repository contains a package for asynchronous user managment and a docker-compose container for setting up it's infrastructure.

## Features

- Asynchronous user management system.
- Docker Compose setup for easy deployment and development.
- Utilizes Python Poetry for managing dependencies and virtual environment.

## Prerequisites

- Docker: Ensure you have Docker installed on your system.
- Docker Compose: Ensure you have Docker Compose installed on your system.
- Poetry: For develpment.

## Setup

1. Clone this repository to your local machine:

```
git clone https://github.com/your-username/async-user-management.git
```

2. Navigate to the project directory:

```
cd async-users
```

3. Run the following command to build and start the Docker containers for development:


```
docker-compose --profile dev up --build
```

This will setup a postgresql database, and other dependencies, (redis for sessions and rabbitmq for messaging in the future).

WARNING: This system is in development stage, is not ready for production yet. 

4. Once the containers are up and running, you can access the application at `http://localhost:8000`.

## Usage

The system comes with a ready to use, jwt authentication fastapi router, you can plug-and-play ite it in your fastapi-app like in following example:

```python
from fastapi import FastAPI, Request
from fastapi import Depends
from fastapi.middleware.cors import CORSMiddleware
from users.auth.endpoints import Auth
from users.auth.settings import Settings

database_url = "your-database-url"

api = FastAPI(root_path="/api")
api.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

auth = Auth(settings=Settings(database_uri=database_url, testing_mode=True, auth_api_prefix='/auth'))
auth.mount(api)

@api.get('/')
async def hello(bearer: str = Depends(auth.bearer)):
    return {'message': 'Hello, World!'}   # Protected route by a jwt token. 

```
The user package also have an accounts domain model, and it's repository, so you can build your own authentication logic with it, like the following:

```python
from users.auth import exceptions
from users.auth.settings import Settings
from users.auth.adapters import Accounts

accounts = Accounts(settings=Settings(database_uri=database_url, testing_mode=True, auth_api_prefix='/auth'))

async with accounts:
    account = await accounts.create(username='test', password='yourpassword') # Here you can access the aggregate root
    #Your logic here

```

I will add support for different types of authentication soon, like email passwords, phone numbers, social providers, etc.
Also I will be adding soon a message queue to the Account aggregate root, so you can extend it with your own events and handlers.

## Contributing

Contributions are welcome! Feel free to open issues or pull requests for any improvements or features you'd like to see in this project.
Make sure to use the ```Setting(test_mode=True)``` so transactions are rolledback when exit the unit of work, event after you commit them. 
There is a workflow for running your integration tests in github actions. You can run your tests in the docker compose container with the command:

```
docker-compose --profile tests up --build --exit-code-from python-tests
```


## License

This software is provided "as is," without warranty of any kind, express or implied. You are solely responsible for the usage of this software. The author(s) of this software shall not be liable for any damages or liabilities arising from the use, operation, or performance of this software.

Please use this software responsibly and in accordance with any applicable laws and regulations.

This project is licensed under the [MIT License](LICENSE).
Feel free to customize it according to your project's specific requirements and infrastructure!
