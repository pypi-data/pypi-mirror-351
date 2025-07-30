# Mediascout ORD API client

Unofficial python client for [ORD Mediascout API](https://demo.mediascout.ru/swagger/index.html).

## Installation

```bash
pip install ord-mediascout-client
```

## Usage

```python
from ord_mediascout_client import ORDMediascoutClient, \
    ORDMediascoutConfig, CreateClientRequest, \
    ClientRelationshipType, LegalForm

config = ORDMediascoutConfig(
    url='http://localhost:5000',
    username='username',
    password='password',
)

api = ORDMediascoutClient(config)

client_dto = CreateClientRequest(
    createMode=ClientRelationshipType.DirectClient,
    legalForm=LegalForm.JuridicalPerson,
    inn="1234567890",
    name="Test Client",
    mobilePhone="1234567890",
    epayNumber=None,
    regNumber=None,
    oksmNumber=None
)

response_client_dto = api.create_client(client_dto)
```

## Testing

Get credentials for accessing https://demo.mediascout.ru/
and put them into .env file (see .env.example.env)

First setup virtual environment (once):
```bash
pipenv install --dev
pipenv install -e .
```

To run tests:
```bash
pipenv shell
pytest
```


## Packaging

```bash
pipenv install --dev
pipenv shell

# update version
vi pyproject.toml

# clean up files from dist/* before deploy not to upload old ones
# rm dist/*

# create new build
python -m build

# upload fresh build
python -m twine upload dist/*
```
