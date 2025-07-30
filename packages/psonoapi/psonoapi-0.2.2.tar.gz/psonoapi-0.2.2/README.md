# Psono python module
A Python client library and command-line interface for Psono password manager.



This module has been developed by http://www.cybersecure.com/ . We provide managed backups and data resilience.

## Installation

```bash
pip install psonoapi
```

Or install from source:

```bash
git clone https://gitlab.com/cyber-secure-public/psono-python-module.git
cd psono-python-module
pip install -e .
```

## Quick Start

### 1. Configuration / authentication

#### For the CLI 
```bash
psono configure
```

This will prompt you for:
- Server URL
- API Key ID
- Private Key
- Secret Key

####  Using Environment Variables (Recommended) - CLI and module.

Instead of storing credentials in the config file, you can use environment variables:

server config:
```bash
export PSONO_API_SERVER_URL=https://psono.org.com/server
export PSONO_API_SERVER_PUBLIC_KEY=
export PSONO_API_SERVER_SIGNATURE=
```

credentials:
```bash
export PSONO_API_KEY_ID='your-key-id'
export PSONO_API_PRIVATE_KEY='your-private-key'
export PSONO_API_SECRET_KEY='your-secret-key'
```

## Usage
### CLI 

```bash
# Check connection status
psono status

# List all secrets
psono secret list

# List secrets in a specific folder
psono secret list /websites

# Get a specific secret
psono secret get /websites/github

# Show password in plain text
psono secret get /websites/github --show-password
```

### Module
```python
import psonoapi

# This connects to the psono public server by default.
psonoserver=psonoapi.PsonoServerConfig(key_id='b3b5c964-50d2-40d7-a0f0-69ae43c498d3',
                                    private_key='test'
                                    secret_key='test')
psono = psonoapi.PsonoAPI(serverconfig=psonoserver)

# getting a secret (this requires full api)
mysecret = psono.get_path('sharename/foldername/secretname')

# getting a secret 
mysecret = psono.get_secret(secret_id='b3b5c964-50d2-40d7-a0f0-69ae43c498d3')

# Getting a list of secrets that apply to a urlfilter:
mysecrets = psono.search_urlfilter('example.com')

# Updating (works as long as you have write permissions)
mysecret.title = 'I want a new title'
psono.update_secret(mysecret)

# You could also use write_secret instead
psono.write_secret(mysecret)

# Creating a new secret
newsecret = psono.generate_new_secret('website_password') # must be one of psonoapi.psono_type_list
newsecret : psonoapi.models.PsonoApplicationPassword # set the type to make life easy for yourself.
newsecret.path = 'existingfolder/newfolder/secretname'
newsecret.password = '1234'
newsecret.username = 'myusername'
newsecret.title = 'My special new secret'
psono.write_secret(newsecret)
```

## CLI Usage


### Basic Commands

```bash
# Check connection status
psono status

# List all secrets
psono secret list

# List secrets in a specific folder
psono secret list /websites

# Get a specific secret
psono secret get /websites/github

# Show password in plain text
psono secret get /websites/github --show-password
```

### Creating Secrets

```bash
# Interactive mode
psono secret create /websites/github --interactive

# Create with JSON data
psono secret create /websites/github --data '{
  "username": "myuser",
  "password": "mypass",
  "url": "https://github.com"
}'

# Create different types
psono secret create /notes/meeting --type note --interactive
psono secret create /cards/visa --type credit_card --data '{"number": "1234", "cvc": "123"}'
```

### Updating and Deleting

```bash
# Update a secret
psono secret update /websites/github --data '{"password": "newpass"}'

# Delete a secret
psono secret delete /websites/github
```

### Searching

```bash
# Search by title
psono secret search github

# Search in specific field
psono secret search example.com --field url

# Search by type
psono secret search "" --type website_password
```

### Import/Export

```bash
# Export all secrets to JSON
psono export -o backup.json

# Export without passwords
psono export -o backup.json

# Export to CSV
psono export -o backup.csv --format csv

# Import from file
psono import -i backup.json

# Dry run import (preview changes)
psono import -i backup.json --dry-run
```

### URL Matching

```bash
# Find credentials for a URL
psono find-by-url github.com
```

## CLI Configuration

The CLI stores its configuration in `~/.psono/config.json`. The configuration file contains:

```json
{
  "server_url": "https://psono.example.com/server",
  "ssl_verify": true
}
```

## API Usage

```python
from psono import PsonoAPI

# Initialize client
api = PsonoAPI({
    'key_id': 'your-key-id',
    'private_key': 'your-private-key',
    'secret_key': 'your-secret-key',
    'server_url': 'https://psono.example.com/server'
})

# Create a password
from psono.models import PsonoWebsitePassword

password = api.generate_new_secret('website_password')
password.title = 'GitHub'
password.username = 'myuser'
password.password = 'securepass123'
password.url = 'https://github.com'
password.path = '/websites/github'

api.write_secret(password)

# Get a secret
secret = api.get_path('/websites/github')
print(f"Username: {secret.username}")

# Search by URL
matches = api.search_urlfilter('github.com')
for match in matches:
    print(f"Found: {match.title} - {match.username}")

# List folder contents
folder = api.get_path('/websites')
for item in folder.items:
    print(f"- {item.name}")

# Update existing secret
secret = api.get_path('/websites/github')
secret.password = 'newpassword123'
api.update_secret(secret)

# Delete a secret
api.delete_secret('/websites/old-site')
```

### Secret Types

The following secret types are supported:

- `website_password` - Website credentials with URL
- `application_password` - Application credentials
- `note` - Secure notes
- `credit_card` - Credit card information
- `bookmark` - Bookmarks
- `environment_variables` - Environment variables
- `totp` - TOTP/2FA codes
- `ssh_key` - SSH keys
- `mail_gpg_own_key` - GPG keys
- `elster_certificate` - Elster certificates

### Advanced Usage

#### Using Custom Fields

```python
# Add custom fields to any secret
secret = api.get_path('/websites/example')
secret.custom_fields = [
    {'name': 'API_KEY', 'type': 'text', 'value': 'abc123'},
    {'name': 'Region', 'type': 'text', 'value': 'us-east-1'}
]
api.update_secret(secret)

# Access custom fields
print(secret.get_custom_field('API_KEY'))  # 'abc123'
```

#### Working with Shares

```python
# Get shared stores (A 'share' is a special type of datastore)
datastore = api.get_datastore()
for share in api.get_sharelist(datastore):
    share_store = api.get_share(share)
    print(f"Share: {share.name}")
```

#### Batch Operations

```python
# Bulk create secrets
secrets = [
    {
        'type': 'website_password',
        'path': f'/websites/{site}',
        'username': f'user@{site}',
        'password': 'temp123',
        'url': f'https://{site}'
    }
    for site in ['example.com', 'test.com', 'demo.com']
]

for secret_data in secrets:
    api.write_secret(secret_data)
```

