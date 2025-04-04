# FinTrack

FinTrack is a personal finance management application that helps users track their income, expenses, savings goals, and budgets. It provides a structured database schema for managing financial data and supports seamless migrations for database setup.

## Features

- User management with secure password storage.
- Categorization of income and expenses.
- Budget tracking with start and end dates.
- Savings goal management.
- Database migrations for easy setup.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/aluriDevAnanth/FinTrack
   cd FinTrack

   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables in a .env file:

   ```bash
   HOST=your_database_host USER=your_database_user PASSWORD=your_database_password DATABASE=your_database_name
   ```

4. Run database migrations:
   ```bash
   python ./db/migrations.py
   ```

## Usage

- Run the application:
  ```bash
  python main.py
  ```

## Project Structure

```bash
.
├── db/
│   ├── [db.py]
│   ├── [migrations.py]
├── [main.py]
├── [requirements.txt]
├── .env
└── [README.md]
```

## Requirements

- Python 3.8+
- MySQL database
