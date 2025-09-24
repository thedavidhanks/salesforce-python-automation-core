# SALESFORCE PYTHON AUTOMATE CORE
This project is intended to be used to start a python based salesforce automation.  

# Installation
When using this project to begin a new python based Salesforce automate, 

1. Make your own project
- Clone or Fork this project
- Remove the remotes.
- Create your own remotes

2. [Create a JWT to connect with](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_auth_key_and_cert.htm)
3. [Create a connect app in your org](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_auth_connected_app.htm)
4. Add your server.key .  Add the key file to the location file to resources/keys directory
5. Setup .env file
copy .env-tempalte as .env and setup the environment variables

- **SSL_SERVER_KEY** - an ssl key generated used by the sf org --client-id param    
  - [create a cert](https://help.salesforce.com/s/articleView?id=xcloud.security_keys_creating.htm&type=5)  
  - [sf cmd](https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/cli_reference_org_commands_unified.htm#cli_reference_org_login_jwt_unified)
- **CLIENT_ID** - consumer key from connect app
- **SERVER_KEY_FILE** - name and location of the of the JWT key file used to create the signing cert.
- [Read more about it](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_auth_key_and_cert.htm)
Example
```
SF_USERNAME=user@rice.edu
SERVER_KEY_FILE=./resources/keys/server.key
CLIENT_ID=3MVG9kBt168mda---REALLY LONG MIX OF LETTERS AND NUMS--3n8wYF
```
6. Start your project in a VS Code container
7. Verify login worksp
`$ python main.py`


# DEVELOPMENT
This project is intended to be developed in a container utilzing VS code with the devcontainers extension.

The development container will do the following:
- Use the image mcr.microsoft.com/devcontainers/python:1-3.12-bullseye
- Install requirements.txt
- Install salesforce cli

## Development configuration
In order to use the container you'll need to do the following:
- Use VS Code with the Dev Containers extension enabled
- Set the environment variable BACKUPS_DIR
- Start docker desktop
- CTL-SHIFT-P -> "Dev Containers: Open Folder in container"

# Updating the project
Fork the project, make some changes, initiate a pull request, wait, wait, wait...

