#!/bin/bash

echo "🔧 Initializing database..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
until docker exec mlops_postgres pg_isready -U admin; do
  sleep 1
done

echo "✅ PostgreSQL is ready!"

# Run Alembic migrations INSIDE the backend container
echo "🚀 Running database migrations..."
docker exec -it mlops_backend alembic upgrade head

echo "✅ Database initialized successfully!"