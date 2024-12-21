db-down:
	@alembic downgrade -1

db-up:
	@alembic upgrade head

db-migrate:
	@read -p "Enter migration name: " migration_name; \
	alembic revision -m "$$migration_name"
