db-down:
	@alembic downgrade -1

db-up:
	@alembic upgrade head

db-migrate:
	@read -p "Enter migration name: " migration_name; \
	alembic revision -m "$$migration_name"

dev:
	@echo "Running the server in dev mode..."
	@bash scripts/dev.sh 

prod:
	@echo "Running the server in prod mode..."
	@bash scripts/prod.sh