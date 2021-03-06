# Online shop
## Project description
This is an online shop for handmade goods. It is developed in Django + DRF + PostgreSQL.

## Workflow example

### Prerequisites
1. Git
1. Python3
1. PostgreSQL

### Step 1: Creating PostgreSQL database through the command line
1. Open the PostgreSQL shell and enter default database (`postgres`) and default user (`postgres`)
1. Create a new database using the following command:  
`CREATE DATABASE your_db_name;`
1. Create a user for your new database:  
`CREATE USER <your_name> WITH PASSWORD '<your_user_password>';`
1. Set a few connection parameters for the new database user:  
   ```postgresql
   ALTER ROLE <your_name> SET client_encoding TO 'utf8';
   ALTER ROLE <your_name> SET default_transaction_isolation TO 'read committed';
   ALTER ROLE <your_name> SET timezone TO 'UTC';
   ```
   - In the first line you are setting the default encoding to UTF-8 expected by Django.  
   - With the second line you are also setting the default transaction isolation scheme to “read committed”, that blocks reads from uncommitted transactions.
   - Finally, by default Django timezone is UTC we are setting our database’s timezone to UTC.
1. Grant your new user access to the database you created earlier:  
    ```postgresql
    GRANT ALL PRIVILEGES ON DATABASE your_db_name TO <your_name>;
    ALTER USER <your_name> CREATEDB;
    ```
   - In the first line you are granting your user all permissions on your database.
   - With the second line you are also granting your user permission to create databases. This is necessary to run the tests because the test database is created under your user during the tests and after all tests are finished it is deleted. 

### Step 2: Cloning the project, creating a virtual environment & installing necessary Python packages
1. Clone the project and get inside:  
    ```shell script
    git clone https://github.com/uladzislau-zhurauski/online-shop.git
    cd online-shop
    ```
1. Create virtual env:  
`python3 -m venv venv`
1. Activate virtual env:  
On Windows: `venv\Scripts\activate.bat`  
On Linux: `source venv/bin/activate`
1. Install the required python packages:
`pip install -r requirements.txt`

### Step 3: Setting up the project
1. Set environment variables for the secret_key and the database user password.
   1. Create a `.env` file in the project root.
   1. Open [this django secret key generator](https://miniwebtool.com/django-secret-key-generator/) or any other and generate a secret key.
   1. Put the environment variables in the `.env` file as follows:  
       ```text
       SECRET_KEY=your_generated_secret_key  
       DB_PASSWORD=your_user_password
       ```
1. Navigate to onlineshop/settings.py. In the DATABASES section, you’ll see the code snippet below.  
    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'online_shop',
            'USER': 'online_shop_user',
            'PASSWORD': os.environ['DB_PASSWORD'],
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
    ```
1. Set you database and user credentials in the corresponding fields, besides the password as it was configured in the `.env` file:
    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'your_db_name',
            'USER': 'your_name',
            'PASSWORD': os.environ['DB_PASSWORD'],
            'HOST': 'localhost',
            'PORT': '',
        }
    }
    ```
   PORT can be empty or contain the port your PostgreSQL is running on.
1. Apply project migrations  
`python manage.py migrate`

### Step 4: Run the project
1. Start the server by running this command:  
`python manage.py runserver`

## Launching tests

### Prerequisites
1. You have fully completed [workflow example](#workflow-example).
1. You are in the root of the project and have activated virtual env as described in [Step 2](#step-2-cloning-the-project-creating-a-virtual-environment--installing-necessary-python-packages) of workflow example.

### Step 1: Run tests
1. The tests are written with `pytest`, so all the options of [this testing tool](https://docs.pytest.org/en/stable/) are available. To just run all tests, type `pytest`. You can check out other options [here](https://docs.pytest.org/en/stable/usage.html#specifying-tests-selecting-tests).

### Step 2: View code coverage report
1. After running tests, the coverage report is generated. It will create a folder named `htmlcov` in the project root. You can open the `index.html` file in your browser and check the coverage.

## Troubleshooting
1. If you are having trouble installing the `psycopg2` package while running `pip install -r requirements.txt`, check [the build prerequisites](https://www.psycopg.org/docs/install.html#build-prerequisites).
