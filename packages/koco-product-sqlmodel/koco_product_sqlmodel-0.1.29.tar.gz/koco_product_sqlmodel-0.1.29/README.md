# koco-product-sqlmodel

This project separates the product describing SQLMODEL from other modules making later use of it. It shall be implemented into the CatalogDB-project and into a separate API project.

## Scope

The module will contain all necessary *sqlmodel*-classes and functions to make an interaction with a KOCO-product-database possible. It shall be available under MIT-license on *pip*.

## Dependencies

The module depends on Tiangolo's [sqlmodel](https://sqlmodel.tiangolo.com/)-package, which is also licensed under [MIT-License](https://github.com/fastapi/sqlmodel/blob/main/LICENSE).


## Environmental Variables
Database information and credentials are provided as environmental variables. Following variables are defined:

```
MARIADB_USER=the_db_user_name
MARIADB_PW=the_db_user_password
MARIADB_URI=the_mariadb_uri
MARIADB_DATABASE=name_of_the_product_database
MARIADB_CONNECTOR_STRING=mariadb+mariadbconnector://${MARIADB_USER}:${MARIADB_PW}@${MARIADB_URI}/${MARIADB_DATABASE}
FASTAPI_SECURITY_SECRET_KEY=generate a key with "openssl rand -hex 32"
DB_BACKUP_FOLDER_URL="PATH_TO_BACKUP_FOLDER" #Note the folder must exist. It will not be created by the app. 
PRODUCT_FILE_FOLDER="PATH_TO_PRODUCT_FILES" #Folder contains all product files with blake2shashed filename.
````

There is an ```.env_example```-file available in the repository.