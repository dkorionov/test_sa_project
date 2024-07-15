# SA-Django test project

### Create .env file using .env.example

### Run project

```bash
make build
make up
make migrate
```

- http://localhost:8000/api/v1/swagger/ to see the API documentation
- http://localhost:8000/admin/ to see the admin panel

### Create superuser

```bash
make superuser
```

### Run tests

```bash
make test
```

### Load fixtures

```bash
make fixtures
```

### Down project

```bash
make down
```

