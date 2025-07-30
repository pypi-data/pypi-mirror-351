# Brivo Smarthome Python Client

A Python client library for communicating with Brivo Smarthome, providing an easy interface for managing authentication and
interacting with Brivo's API.

## Installation

```sh
pip install brivo-smarthome
```

## Example Usage

```python
from brivo import App

# Initialize the client
# Username and password can be set with environment variables 'BRIVO_USERNAME' and 'BRIVO_PASSWORD'
brivo = App(username='your_user_name', password='your_password')

# Get companies
companies = brivo.my_company_ids()

for company_id in companies:
    for user in brivo.company_users(company_id):
        print(user)
```

## Contributing

Contributions are welcome! Feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License.
