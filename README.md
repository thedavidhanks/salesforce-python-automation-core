# SALESFORCE PYTHON AUTOMATE CORE
This project is intended to be used to start a python based salesforce automation.  

# Installation
When using this project to begin a new python based Salesforce automation, 

1. Make your own project
    - Clone or Fork this project  
    - Remove the remotes.  
    - Create your own remotes  

2. [Create a JSON Web Token (JWT)](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_auth_key_and_cert.htm)  
    - Add the server.key file to the location file to resources/secrets directory
3. [Create a connect app in your org](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_auth_connected_app.htm)
    - Be sure to add the server.crt file to the application.  App Manager -> Edit (from App drop down) -> Choose File (under API/Use digital signatures)
4. Get the Consume Key (Setup -> App Manager -> View (from App drop down) -> API - Manage Consume Details)
5. Create a user to access the application.  NOTE: It may be necessary to log in to the org as this user once.
5. Ensure that a permission set (or profile) is assigned to the app and the user specified by {SF_USERNAME}
6. Setup .env file
copy .env-tempalate as .env and setup the environment variables
    - **SF_USERNAME** - username for your salesforce org  
    - **SERVER_KEY_FILE** - name and location of the of the JWT key file used to create the signing cert.  [Read more about it](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_auth_key_and_cert.htm)  
    - **CLIENT_ID** - consumer key from connect app  
Example
```
SF_USERNAME=user@rice.edu
SERVER_KEY_FILE=./resources/keys/server.key
CLIENT_ID=3MVG9kBt168mda---REALLY LONG MIX OF LETTERS AND NUMS--3n8wYF
```
6. Start your project in a VS Code container
7. Verify login works
`$ python main.py`

# DEVELOPMENT
This project is intended to be developed in a container utilzing VS code with the devcontainers extension.

The development container will do the following:
- Use the image specifed in .devcontainer/Dockerfile
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

# References
  [sf cmd](https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/cli_reference_unified.htm)   
  [sf login with JWT](https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/cli_reference_org_commands_unified.htm#cli_reference_org_login_jwt_unified)

# Credits
  This repository was started by using [https://github.com/thedavidhanks/salesforce-python-automation-core](https://github.com/thedavidhanks/salesforce-python-automation-core)