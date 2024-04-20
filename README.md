# Async User Management System with python

This repository contains a package for asynchronous user managment and a docker-compose container for setting up it's infrastructure.
Since it has a carefully designed event driven architecture, it's completly extensible, there are not first citizen class authentication methods, so feel free to add your own, like phone message, email auth, etc.

## Features

- Asynchronous user management system (Only authentication for now).
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

If you want to test locally:

```
docker-compose --profile tests up --build --exit-code-from python-tests
```


This will setup a postgresql database, and other dependencies, (redis for user activity and rabbitmq for messaging in the future).

WARNING: This system is in development stage, is not ready for production yet. 

4. Once the containers are up and running, you can access the application at `http://localhost:8000`.

## Usage

The system comes with a ready to use, jwt authentication fastapi router, you can plug-and-play it in your fastapi-app like in following example:

```python
from fastapi import FastAPI, Request
from fastapi import Depends
from fastapi.middleware.cors import CORSMiddleware
from users.settings import Settings
from users.auth.endpoints import Auth

database_url = "your-database-url"

api = FastAPI(root_path="/api")
api.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

auth = Auth(settings=Settings(database_uri=database_url, testing_mode=True, auth_api_prefix='/auth'))
auth.mount(api)

@api.get('/')
async def hello(bearer: str = Depends(auth.bearer)):
    return {'message': 'Hello, World!'}   # Protected route by a jwt token. 

```

If you want to use only some auth functions with your own routes, you can access auth methods easily:

```python

@api.post('/my-auth-route')
async def auth_route(self, form: Annotated[OAuth2PasswordRequestForm, Depends()])
    return await auth.login(form)

```

You can also, write your own logic using the domain model:

```python

from users.settings import Settings
from users.auth import exceptions
from users.auth.repository import Accounts
from users.auth.models import Credentials

accounts = Accounts(settings=Settings(database_uri=database_url, testing_mode=True))

async with accounts:
    account = await accounts.create() # Here you can access the aggregate root
    account.credential = Credential(username='username', password='password')
    account.email = 'test@email.com'  # Seems easy but there is some dark wizzard magic going on...
    await account.save() #Value objects are created into the root using events, and the save method call the handlers.

async with accounts:
    account = await accounts.read(email='test@email.com')
    account.credential = Credential(username='other-username', password='other-password')
    await account.save() #Same here, to root decides to use an update handler instead of a add handler.

```

## Contributing

Contributions are welcome! Feel free to open issues or pull requests for any improvements or features you'd like to see in this project.

I will add support for different types of authentication soon, like email passwords, phone numbers, social providers, etc.
If you want to contribute, go into auth/repository/accounts and implement the handlers with the ones you need.

There is a dictionary like this: 

```python
    self.handlers: Dict[str, List[Callable]] = {
        'credential-added': [handlers.AddCredential(self.credentials)],
        'credential-updated': [handlers.UpdateCredential(self.credentials)], #TODO: Send email notification on credential update
        #TODO: Add handlers for the following events
        'email-added': [],
        'email-updated': [],
        ...
    }
```

Of stuff that has to be implemented. 

Make sure to use the ```Setting(test_mode=True)``` so transactions are rolledback when exit a context manager, even if you commit them. 
There is a workflow for running your integration tests in github actions. You can run your tests in the docker compose container with the command:

```
docker-compose --profile tests up --build --exit-code-from python-tests
```


## License

This software is provided "as is," without warranty of any kind, express or implied. You are solely responsible for the usage of this software. The author(s) of this software shall not be liable for any damages or liabilities arising from the use, operation, or performance of this software.

Please use this software responsibly and in accordance with any applicable laws and regulations.

This project is licensed under the [MIT License](LICENSE).
Feel free to customize it according to your project's specific requirements and infrastructure!
