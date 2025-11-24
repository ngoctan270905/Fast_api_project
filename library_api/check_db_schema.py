import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text, inspect
from sqlmodel import SQLModel # Assuming SQLModel base is needed for reflection

# --- Configuration from alembic.ini ---
# Make sure this matches the sqlalchemy.url in your alembic.ini
DATABASE_URL = "mysql+aiomysql://root:1@192.168.6.181:3308/library_db"
# If you used mysql+pymysql, change to that. For this check, we'll use aiomysql if possible
# If the async engine fails, you might need to use a synchronous one for this simple check.
# For simplicity, we'll use the async one.

async def check_db_schema():
    print(f"Connecting to database: {DATABASE_URL}")
    engine = create_async_engine(DATABASE_URL, echo=True)

    async with engine.connect() as connection:
        # Check Alembic version
        result = await connection.execute(text("SELECT version_num FROM alembic_version;"))
        alembic_version = result.scalar_one_or_none()
        print(f"\nCurrent Alembic version: {alembic_version}")

        # List all tables
        inspector = inspect(connection)
        table_names = await inspector.get_table_names()
        print(f"\nTables in database: {', '.join(table_names)}")

        # Check for oauthaccount table
        if "oauthaccount" in table_names:
            print("\n'oauthaccount' table found!")
            columns = await inspector.get_columns("oauthaccount")
            print("  Columns in 'oauthaccount' table:")
            for col in columns:
                print(f"    - {col['name']}: {col['type']}")
        else:
            print("\n'oauthaccount' table NOT found.")

        # Check 'user' table for 'hashed_password' column nullability
        if "user" in table_names:
            print("\n'user' table found. Checking 'hashed_password' column...")
            columns = await inspector.get_columns("user")
            for col in columns:
                if col['name'] == 'hashed_password':
                    print(f"  'hashed_password' column in 'user' table is nullable: {col['nullable']}")
                    break
            else:
                print("  'hashed_password' column NOT found in 'user' table.")
        else:
            print("\n'user' table NOT found.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_db_schema())
