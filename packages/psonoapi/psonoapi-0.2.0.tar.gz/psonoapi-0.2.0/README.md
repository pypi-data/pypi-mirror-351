# Psono python module

This module is intended to allow you to interface with psono, a self hosted/cloud hosted open source secret manager.

This module has been developed by http://www.cybersecure.com/ . We provide managed backups and data resilience.

## Authentication

You can either set it in the code as per below, or you can set it in the environment, and it will login automagically.
```sh
export PSONO_API_KEY_ID=
export PSONO_API_PRIVATE_KEY=
export PSONO_API_SECRET_KEY=
export PSONO_API_SERVER_URL=https://psono.org.com/server
export PSONO_API_SERVER_PUBLIC_KEY=
export PSONO_API_SERVER_SIGNATURE=
```

## Simple examples
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