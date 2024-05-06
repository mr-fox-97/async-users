**User Management Domain Model**

A Python-based domain model for user management, featuring a robust and scalable architecture. This project provides a foundation for building user-centric applications, with a focus on simplicity, flexibility, and testability.

Here is an updated version of the GitHub description:

**Quick tour**

This project provides a domain model for user management. The domain model is built on an event-driven architecture, allowing for loose coupling between components and enabling a more scalable and resilient system. The architecture is designed with microservices in mind, making it easy to integrate with other services and systems, enabling seamless communication between microservices, event sourcing and auditing.

For using it you create an application, with the services you need. Example
    
```python

from src.services import Settings, Application
from src.users imprt Users

settings = Settings(orm=SQLAlchemySettings(uri="postgresql://postgres:postgres@localhost:5432/postgres"))

application = Application(settings)

async with Users(bind=application) as users:
    user = await users.create(name="John Doe")
    user.password = "password" # This will enqueue an event and dispatch it to the event handlers when the user is saved
    await users.save(user) # Here all mutations of the user model are persisted in the database in a single transaction.

async with Users(bind=application) as users:
    user = await users.read(name="John Doe")
    assert await user.verify(password = "password") #The user uses a command handler to verify it against a DAO or service
    print(user.password) #prints "******" The user don't store any info from passwords.

```

The idea of the context manager is to keep consistency boundaries in the aggregate, so if something goes wrong, the context manager will rollback the transaction and the user will not be persisted in the database.

Handlers are also easily injected into the Users service, this will allow event sourcing and auditing for the events that the user of
the system wants to track, like password changing, emails added, etc.

```python

application.bus.subscribe('email-added', lambda event: print(f'Send email notification to user {event.publisher.id}'))

users = Users(bind=aplication)
users.subscribe('phone-added', lambda event: user.session.execute('INSERT INTO phone_audit VALUES (:phone)', {'phone': event.payload}))
users.subscribe('email-added', lambda event: raise Exception('Email had a problem'))
async with users:
    user = await users.create(name="John Doe")
    user.add_phone("123456789")
    user.add_email("jhony@test.com")
    await users.save() # The transaction will be rolled for the user and no data will be persisted in the database

```

username and passwords are not a hard requirement, the idea is to have a flexible system that can be extended to support new authentication methods as needed.

**Key Features**

* **Flexible User Registration**: Register users with a variety of authentication methods, not limited to traditional username and password combinations. Easily extend the system to support new authentication methods as needed.
* **Event-Driven Architecture**: Built on an event-driven architecture, allowing for loose coupling between components and enabling a more scalable and resilient system. This architecture enables easy extension of the system through the addition of new event handlers, which can react to specific events and perform custom logic.
* **Microservices-Ready**: Designed with microservices in mind, making it easy to integrate with other services and systems. The event-driven architecture and decoupled repositories and adapters enable seamless communication between microservices.
* **Decoupled Repositories and Adapters**: Interact with various data storage systems, such as databases and file systems, using decoupled repositories and adapters. This allows for easy switching between different storage systems or adding new ones as needed.
* **UnitOfWork Pattern**: Implementing the UnitOfWork pattern to manage transactions and ensure data consistency.
* **Application Services**: A set of application services for performing common user management operations, such as user creation, authentication, and password verification.
* **Test-Driven Development**: A comprehensive test suite using Pytest, ensuring the correctness and reliability of the domain model.
* **Extensibility through Event and Command Handlers**: Easily extend the system by adding new event handlers, which can react to specific events and perform custom logic. Command handlers can also be added to handle specific commands, such as user registration or password reset. This allows for a high degree of customization and flexibility, making it easy to adapt the system to specific business needs.

With this architecture, you can easily add new features or functionality by:

* Creating new event handlers to react to specific events, such as user registration or password reset.
* Implementing new command handlers to handle specific commands, such as user creation or authentication.
* Adding new adapters to interact with different data storage systems or services.
* Extending the application services to perform new user management operations.

This flexibility and extensibility make it easy to adapt the system to specific business needs and ensure that it remains scalable and maintainable over time.

**Testing and Deployment**
This project uses GitHub Workflows to automate testing and deployment. The workflow includes running Pytest tests, including transactional integration tests, to ensure the correctness and reliability of the code.

**Getting Started**

To run the tests, execute the following commands, be sure to have docker installed in your system:

1. `docker-compose --profile tests up --build --exit-code-from python-tests`
2. `docker compose down -v --remove-orphans`

This will spin up a Docker container with the necessary dependencies, run the tests, and then tear down the container.


**Contributing**

Contributions are welcome If you'd like to contribute to this project, please fork the repository, make your changes, and submit a pull request.

**License**

This project is licensed under the [MIT License](LICENSE).

I hope this helps Let me know if you need any further assistance.


## License

This software is provided "as is," without warranty of any kind, express or implied. You are solely responsible for the usage of this software. The author(s) of this software shall not be liable for any damages or liabilities arising from the use, operation, or performance of this software.

Please use this software responsibly and in accordance with any applicable laws and regulations.

This project is licensed under the [MIT License](LICENSE).
Feel free to customize it according to your project's specific requirements and infrastructure!
