# DJANGO BASE PROJECT


### Steps to start a Django Project

- Activate Virtual Enviornment
- pip install poetry
- poetry install ( to install all pre-installed python modules like django, django restframework etc )
- Generate fernet key using general.encryptions.generate_key method and add generated key to secret.key file
- Run --> poetry run python .\manage.py makemigrations (to generate migrations)
- Run --> poetry run python .\manage.py migrate (to migrate)
- Run --> poetry run python .\manage.py runserver (to run development server)
- Run --> poetry add <Package-Name> ( to install python module )
- Run --> poetry remove <Package-Name> ( to uninstall python module )
- You can customize this project as you need

Refer https://rogue-tea-117.notion.site/BACKEND-RESPONSES-648fbd62d74149ffb69dc5329a00cc2b for response data format