from db import create_connection, database

print(database)


def execute_migration(conn, sql):
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        print("Migration executed successfully")
    except Exception as e:
        print(f"Error executing migration: {e}")
        conn.rollback()
    finally:
        if cursor:
            cursor.close()


def run_migrations():
    conn = create_connection()
    if not conn:
        print("Failed to create database connection")
        return

    try:
        execute_migration(
            conn,
            """-- sql
                CREATE TABLE IF NOT EXISTS users (
                    user_id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL, 
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                );
            """,
        )

        execute_migration(
            conn,
            """-- sql
                CREATE TABLE IF NOT EXISTS income (
                    income_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    description VARCHAR(255),
                    income_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                );
            """,
        )

        execute_migration(
            conn,
            """-- sql
                CREATE TABLE IF NOT EXISTS expenses (
                    expense_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    description VARCHAR(255),
                    expense_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                );
            """,
        )

        execute_migration(
            conn,
            """-- sql
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                description VARCHAR(255),
                transaction_date DATE NOT NULL,
                type ENUM('income', 'expense') NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
            """,
        )

        execute_migration(
            conn,
            """-- sql
                CREATE TABLE IF NOT EXISTS budgets (
                    budget_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    CHECK (end_date > start_date)
                );
            """,
        )

        execute_migration(
            conn,
            """-- sql
                CREATE TABLE IF NOT EXISTS savings_goals (
                    goal_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    target_amount DECIMAL(10, 2) NOT NULL,
                    current_amount DECIMAL(10, 2) DEFAULT 0.00,
                    target_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                );
            """,
        )

        print("All migrations completed successfully")

    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        if conn:
            conn.close()


run_migrations()
