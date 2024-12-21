# Python Flask Server - Starter Kit

This is a simple Flask server application that demonstrates how to create a RESTful API using Flask. It includes a basic CRUD (Create, Read, Update, Delete) API for managing items.

## Prerequisites

The .venv file is included in the repository, simply

## Installation

1. Clone the repository:

```bash
git clone https://github.com/dimrev/python-flask-app.git
```

2. Navigate to the project directory:

```bash
cd python-flask-app
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Database Migration - Makefile

In order to manage the database migrations, you can follow these steps:

1. Create a new migration file:

```bash
make db-migrate
```

- This will prompt you to enter a migration name `$$migration_name`.
- The migration file will be created in the `db/migrations/versions` directory under `datetimeHash_migration_name.py`.

2. Write the migration code in the new file.

```python
def upgrade() -> None:
    op.create_table(
        "items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("items")
```

- The `upgrade` function contains the SQL commands to create the table.
- The `downgrade` function contains the SQL commands to drop the table.

3. Apply the migration:

```bash
make db-up
```

4. (optional) Rollback the migration 1 step back:

```bash
make db-down
```

### Running the Server

To start the server, run the following command:

```bash
python -m app.main
```

## Structure

```
root/
├── app/
│   ├── api/
│   │   │ Holds all the API routes
│   │   ├── items/
│   │   │   │ Holds the item in a single bundle.
│   │   │   ├── item_controller.py
│   │   │   ├── item_model.py
│   │   │   ├── item_service.py
│   │   │   └── item_schema.py
│   │   ├── finances/
│   │   │   └──...
│   │   └──...
│   │
│   ├── routes/
│   │   │ Holds all the different top level routes of the app, /api, /ws etc.
│   │   ├── api_routes.py
│   │   └── ...
│   │
│   ├── services/
│   │   │ Holds all the app wide services that don't belong in a single bundle
│   │   ├── logger_service.py
│   │   ├── selenium_service.py
│   │   └── ...
│   │
│   ├── utils/
│   │   │ Holds all the app wide utils that don't belong in a single bundle
│   │   ├── api_consts.py
│   │   └── api_utils.py
│   │
│   ├── main.py - App entry point
│   └── __init__.py - App bootstrap
│
├── db/
│   │ Holds the sqlite embedded database
│   ├── migrations/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   ├── versions
│   │   │   ├── e0e9c3c0c7e3_migration.py
│   │   │   └── ...
│   │   └── ...
│   ├── db.py - Singleton class to manage the database connection
│   └── app.db - Database file
│
├── .env
├── Makefile - Makefile for managing the database migrations
├── README.md
├── requirements.txt - Python dependencies
└── run.sh - Script to run the server
```
