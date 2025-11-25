#!/bin/sh

# Chờ MySQL sẵn sàng
echo "Waiting for MySQL..."
for i in $(seq 1 5); do
    mysqladmin ping -h db -uroot -p1 >/dev/null 2>&1 && break
    echo "DB not ready, retrying ($i/5)..."
    sleep 3
done


# Chạy Alembic migrations
echo "Running Alembic migrations..."
alembic upgrade head

# Start Uvicorn
echo "Starting Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
