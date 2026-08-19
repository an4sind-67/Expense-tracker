💰 Expense Tracker

A full-stack personal finance management web application built with **Python, Flask, HTML, CSS, JavaScript, and SQLite**.

Expense Tracker allows users to securely manage their income and expenses, set monthly budgets, and visualize their spending through interactive dashboards and charts.

🚀 Features

🔐 User Authentication
- User registration
- Secure login/logout
- Password hashing
- Protected application routes
- User-specific financial data
- Multi-user data isolation

💸 Expense Management
- Add expenses
- Edit expenses
- Delete expenses
- Categorize expenses
- Record transaction dates
- View recent transactions

💰 Income Management
- Add income
- Categorize income
- Track total income
- View income transactions

Budget Management
- Set monthly budget
- Track monthly spending
- Calculate remaining budget
- Display budget usage percentage
- Visual progress indicator

📊 Dashboard
- Total balance
- Total income
- Total expenses
- Monthly budget
- Recent transactions
- Spending by category
- Monthly spending trends
- Income vs expenses visualization

🔔 User Feedback
- Success notifications
- Error notifications
- Budget update notifications
- Expense operation notifications
- Income operation notifications

🛠️ Tech Stack

Backend
- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login

Frontend
- HTML5
- CSS3
- JavaScript
- Chart.js

Database
- SQLite
- SQLAlchemy ORM

Development Tools
- Visual Studio Code
- Git
- GitHub

🏗️ Project Architecture

```text
Expense-Tracker/
│
├── app.py
├── models.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       ├── dashboard.js
│       └── expenses.js
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── expenses.html
│   ├── income.html
│   ├── budget.html
│   ├── add_expense.html
│   ├── add_income.html
│   └── edit_expense.html
│
└── instance/
    └── expenses.db