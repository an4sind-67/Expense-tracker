from flask import Flask, render_template, request, redirect, url_for, flash, Response
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)
from models import db, User, Expense, Income, Budget
from datetime import datetime, date
from sqlalchemy import inspect, text
import csv
import io


app = Flask(__name__)


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expenses.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Used by Flask-Login to securely manage sessions.
# For a real production deployment, use a strong secret
# stored in an environment variable.
app.config["SECRET_KEY"] = "expense-tracker-development-secret"


db.init_app(app)


# ============================================================
# FLASK-LOGIN CONFIGURATION
# ============================================================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"

login_manager.login_message = None


@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))


# ============================================================
# DATABASE MIGRATION FOR EXISTING DATABASE
# ============================================================

def update_existing_database():

    inspector = inspect(db.engine)

    # Make sure all normal tables exist first.
    db.create_all()


    # --------------------------------------------------------
    # Add user_id to Expense table if it doesn't exist
    # --------------------------------------------------------

    expense_columns = [
        column["name"]
        for column in inspector.get_columns("expense")
    ]

    if "user_id" not in expense_columns:

        with db.engine.connect() as connection:

            connection.execute(
                text(
                    "ALTER TABLE expense "
                    "ADD COLUMN user_id INTEGER"
                )
            )

            connection.commit()


    # --------------------------------------------------------
    # Add user_id to Income table if it doesn't exist
    # --------------------------------------------------------

    inspector = inspect(db.engine)

    income_columns = [
        column["name"]
        for column in inspector.get_columns("income")
    ]

    if "user_id" not in income_columns:

        with db.engine.connect() as connection:

            connection.execute(
                text(
                    "ALTER TABLE income "
                    "ADD COLUMN user_id INTEGER"
                )
            )

            connection.commit()


    # --------------------------------------------------------
    # Add user_id to Budget table if it doesn't exist
    # --------------------------------------------------------

    inspector = inspect(db.engine)

    budget_columns = [
        column["name"]
        for column in inspector.get_columns("budget")
    ]

    if "user_id" not in budget_columns:

        with db.engine.connect() as connection:

            connection.execute(
                text(
                    "ALTER TABLE budget "
                    "ADD COLUMN user_id INTEGER"
                )
            )

            connection.commit()


# ============================================================
# REGISTER
# ============================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if current_user.is_authenticated:

        return redirect(
            url_for("home")
        )


    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )


        # ----------------------------------------------------
        # Basic validation
        # ----------------------------------------------------

        if not username or not email or not password:

            return render_template(
                "register.html",
                error="Please fill in all fields."
            )


        if len(password) < 6:

            return render_template(
                "register.html",
                error="Password must contain at least 6 characters."
            )


        # ----------------------------------------------------
        # Check existing username
        # ----------------------------------------------------

        existing_username = User.query.filter_by(
            username=username
        ).first()


        if existing_username:

            return render_template(
                "register.html",
                error="Username already exists."
            )


        # ----------------------------------------------------
        # Check existing email
        # ----------------------------------------------------

        existing_email = User.query.filter_by(
            email=email
        ).first()


        if existing_email:

            return render_template(
                "register.html",
                error="Email already registered."
            )


        # ----------------------------------------------------
        # Create user
        # ----------------------------------------------------

        user = User(

            username=username,

            email=email

        )

        user.set_password(password)


        db.session.add(user)

        db.session.commit()


        # ----------------------------------------------------
        # Assign old records to first registered user
        # ----------------------------------------------------
        #
        # Your project already contains expenses, income and
        # budget records created before authentication existed.
        #
        # We assign those old records to the first user so
        # your existing data is not lost.
        # ----------------------------------------------------

        if User.query.count() == 1:

            Expense.query.filter_by(
                user_id=None
            ).update(
                {
                    "user_id": user.id
                },
                synchronize_session=False
            )


            Income.query.filter_by(
                user_id=None
            ).update(
                {
                    "user_id": user.id
                },
                synchronize_session=False
            )


            Budget.query.filter_by(
                user_id=None
            ).update(
                {
                    "user_id": user.id
                },
                synchronize_session=False
            )


            db.session.commit()


        # ----------------------------------------------------
        # Login immediately after registration
        # ----------------------------------------------------

        login_user(user)


        return redirect(
            url_for("home")
        )


    return render_template(
        "register.html"
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if current_user.is_authenticated:

        return redirect(
            url_for("home")
        )


    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )


        user = User.query.filter_by(
            email=email
        ).first()


        if user and user.check_password(password):

            login_user(user)


            return redirect(
                url_for("home")
            )


        return render_template(
            "login.html",
            error="Invalid email or password."
        )


    return render_template(
        "login.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
@login_required
def logout():

    logout_user()


    return redirect(
        url_for("login")
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
@login_required
def home():

    # --------------------------------------------------------
    # Get current user's expenses
    # --------------------------------------------------------

    expenses = Expense.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Expense.date.desc()
    ).all()


    # --------------------------------------------------------
    # Get current user's income
    # --------------------------------------------------------

    incomes = Income.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Income.date.desc()
    ).all()


    # ========================================================
    # TOTAL INCOME
    # ========================================================

    total_income = sum(
        income.amount
        for income in incomes
    )


    # ========================================================
    # TOTAL EXPENSES
    # ========================================================

    total_expenses = sum(
        expense.amount
        for expense in expenses
    )


    # ========================================================
    # BALANCE
    # ========================================================

    balance = total_income - total_expenses


    # ========================================================
    # EXPENSES BY CATEGORY
    # ========================================================

    category_totals = {}


    for expense in expenses:

        if expense.category in category_totals:

            category_totals[
                expense.category
            ] += expense.amount

        else:

            category_totals[
                expense.category
            ] = expense.amount


    category_labels = list(
        category_totals.keys()
    )

    category_values = list(
        category_totals.values()
    )


    # ========================================================
    # MONTHLY EXPENSE TOTALS
    # ========================================================

    monthly_totals = {}


    for expense in expenses:

        month_key = expense.date.strftime(
            "%Y-%m"
        )


        if month_key in monthly_totals:

            monthly_totals[
                month_key
            ] += expense.amount

        else:

            monthly_totals[
                month_key
            ] = expense.amount


    monthly_totals = dict(
        sorted(
            monthly_totals.items()
        )
    )


    monthly_labels = list(
        monthly_totals.keys()
    )

    monthly_values = list(
        monthly_totals.values()
    )


    # ========================================================
    # CURRENT MONTH
    # ========================================================

    current_month = date.today().month

    current_year = date.today().year


    # ========================================================
    # CURRENT USER'S BUDGET
    # ========================================================

    budget = Budget.query.filter_by(

        user_id=current_user.id,

        month=current_month,

        year=current_year

    ).first()


    if budget:

        monthly_budget = budget.amount

    else:

        monthly_budget = 0


    # ========================================================
    # CURRENT MONTH EXPENSES
    # ========================================================

    monthly_expenses = sum(

        expense.amount

        for expense in expenses

        if expense.date.month == current_month

        and expense.date.year == current_year

    )


    # ========================================================
    # REMAINING BUDGET
    # ========================================================

    budget_remaining = (

        monthly_budget

        - monthly_expenses

    )


    # ========================================================
    # BUDGET PERCENTAGE
    # ========================================================

    if monthly_budget > 0:

        budget_percentage = (

            monthly_expenses

            / monthly_budget

        ) * 100

    else:

        budget_percentage = 0


    display_percentage = min(

        budget_percentage,

        100

    )


    # ========================================================
    # RECENT TRANSACTIONS
    # ========================================================

    transactions = []


    # Add expenses

    for expense in expenses:

        transactions.append({

            "title": expense.title,

            "category": expense.category,

            "date": expense.date,

            "amount": expense.amount,

            "type": "expense"

        })


    # Add income

    for income in incomes:

        transactions.append({

            "title": income.title,

            "category": income.source,

            "date": income.date,

            "amount": income.amount,

            "type": "income"

        })


    transactions.sort(

        key=lambda transaction:
        transaction["date"],

        reverse=True

    )


    transactions = transactions[:5]


    # ========================================================
    # DASHBOARD
    # ========================================================

    return render_template(

        "index.html",

        expenses=expenses,

        incomes=incomes,

        total_income=total_income,

        total_expenses=total_expenses,

        balance=balance,

        transactions=transactions,

        monthly_budget=monthly_budget,

        monthly_expenses=monthly_expenses,

        budget_remaining=budget_remaining,

        budget_percentage=budget_percentage,

        display_percentage=display_percentage,

        category_labels=category_labels,

        category_values=category_values,

        monthly_labels=monthly_labels,

        monthly_values=monthly_values

    )


# ============================================================
# ADD EXPENSE
# ============================================================

@app.route(
    "/add-expense",
    methods=["GET", "POST"]
)
@login_required
def add_expense():

    if request.method == "POST":

        title = request.form["title"]

        amount = float(
            request.form["amount"]
        )

        category = request.form["category"]

        date_value = datetime.strptime(

            request.form["date"],

            "%Y-%m-%d"

        ).date()


        expense = Expense(

            title=title,

            amount=amount,

            category=category,

            date=date_value,

            user_id=current_user.id

        )


        db.session.add(expense)

        db.session.commit()

        flash("Expense added successfully.", "success")

        return redirect(
            url_for("home")
        )


    return render_template(
        "add_expense.html"
    )


# ============================================================
# EXPENSES PAGE
# ============================================================

@app.route("/expenses")
@login_required
def expenses():

    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    from_date = request.args.get("from_date", "").strip()
    to_date = request.args.get("to_date", "").strip()

    query = Expense.query.filter_by(
        user_id=current_user.id
    )

    if search:
        query = query.filter(
            Expense.title.ilike(f"%{search}%")
        )

    if category:
        query = query.filter(
            Expense.category == category
        )

    if from_date:
        try:
            start_date = datetime.strptime(
                from_date,
                "%Y-%m-%d"
            ).date()

            query = query.filter(
                Expense.date >= start_date
            )

        except ValueError:
            from_date = ""

    if to_date:
        try:
            end_date = datetime.strptime(
                to_date,
                "%Y-%m-%d"
            ).date()

            query = query.filter(
                Expense.date <= end_date
            )

        except ValueError:
            to_date = ""

    expenses = query.order_by(
        Expense.date.desc()
    ).all()

    return render_template(
        "expenses.html",
        expenses=expenses,
        search=search,
        category=category,
        from_date=from_date,
        to_date=to_date
    )

@app.route("/expenses/export")
@login_required
def export_expenses():

    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    from_date = request.args.get("from_date", "").strip()
    to_date = request.args.get("to_date", "").strip()

    query = Expense.query.filter_by(
        user_id=current_user.id
    )

    if search:
        query = query.filter(
            Expense.title.ilike(f"%{search}%")
        )

    if category:
        query = query.filter(
            Expense.category == category
        )

    if from_date:
        try:
            start_date = datetime.strptime(
                from_date,
                "%Y-%m-%d"
            ).date()

            query = query.filter(
                Expense.date >= start_date
            )

        except ValueError:
            pass

    if to_date:
        try:
            end_date = datetime.strptime(
                to_date,
                "%Y-%m-%d"
            ).date()

            query = query.filter(
                Expense.date <= end_date
            )

        except ValueError:
            pass

    expenses = query.order_by(
        Expense.date.desc()
    ).all()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Expense",
        "Category",
        "Date",
        "Amount"
    ])

    for expense in expenses:
        writer.writerow([
            expense.title,
            expense.category,
            expense.date,
            expense.amount
        ])

    response = Response(
        output.getvalue(),
        mimetype="text/csv"
    )

    response.headers["Content-Disposition"] = (
        "attachment; filename=expenses.csv"
    )

    return response


# ============================================================
# EDIT EXPENSE
# ============================================================

@app.route(
    "/edit-expense/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def edit_expense(id):

    expense = Expense.query.filter_by(

        id=id,

        user_id=current_user.id

    ).first_or_404()


    if request.method == "POST":

        expense.title = request.form["title"]

        expense.amount = float(
            request.form["amount"]
        )

        expense.category = request.form["category"]

        expense.date = datetime.strptime(

            request.form["date"],

            "%Y-%m-%d"

        ).date()


        db.session.commit()

        flash(
            "Expense updated successfully.",
            "success"
            )


        return redirect(
            url_for("expenses")
        )


    return render_template(

        "edit_expense.html",

        expense=expense

    )


# ============================================================
# DELETE EXPENSE
# ============================================================

@app.route(
    "/delete-expense/<int:id>"
)
@login_required
def delete_expense(id):

    expense = Expense.query.filter_by(

        id=id,

        user_id=current_user.id

    ).first_or_404()


    db.session.delete(expense)

    db.session.commit()

    flash(
        "Expense deleted successfully.",
        "success"
    )


    return redirect(
        url_for("expenses")
    )


# ============================================================
# ADD INCOME
# ============================================================

@app.route(
    "/add-income",
    methods=["GET", "POST"]
)
@login_required
def add_income():

    if request.method == "POST":

        title = request.form["title"]

        amount = float(
            request.form["amount"]
        )

        source = request.form["source"]

        date_value = datetime.strptime(

            request.form["date"],

            "%Y-%m-%d"

        ).date()


        income = Income(

            title=title,

            amount=amount,

            source=source,

            date=date_value,

            user_id=current_user.id

        )


        db.session.add(income)

        db.session.commit()

        flash(
            "Income added successfully.",
            "success"
        )

        return redirect(
            url_for("home")
        )


    return render_template(
        "add_income.html"
    )


# ============================================================
# INCOME PAGE
# ============================================================

@app.route("/income")
@login_required
def income():

    incomes = Income.query.filter_by(

        user_id=current_user.id

    ).order_by(

        Income.date.desc()

    ).all()


    return render_template(

        "income.html",

        incomes=incomes

    )


# ============================================================
# BUDGET
# ============================================================

@app.route(
    "/budget",
    methods=["GET", "POST"]
)
@login_required
def budget():

    current_month = date.today().month

    current_year = date.today().year


@app.route("/reports")
@login_required
def reports():

    expenses = Expense.query.filter_by(
        user_id=current_user.id
    ).all()

    incomes = Income.query.filter_by(
        user_id=current_user.id
    ).all()

    total_income = sum(
        income.amount
        for income in incomes
    )

    total_expenses = sum(
        expense.amount
        for expense in expenses
    )

    balance = total_income - total_expenses

    transaction_count = (
        len(expenses) + len(incomes)
    )

    category_totals = {}

    for expense in expenses:

        if expense.category in category_totals:

            category_totals[expense.category] += expense.amount

        else:

            category_totals[expense.category] = expense.amount

    category_labels = list(
        category_totals.keys()
    )

    category_values = list(
        category_totals.values()
    )

    monthly_income = {}

    for income in incomes:

        month_key = income.date.strftime(
            "%Y-%m"
        )

        if month_key in monthly_income:

            monthly_income[month_key] += income.amount

        else:

            monthly_income[month_key] = income.amount

    monthly_expenses = {}

    for expense in expenses:

        month_key = expense.date.strftime(
            "%Y-%m"
        )

        if month_key in monthly_expenses:

            monthly_expenses[month_key] += expense.amount

        else:

            monthly_expenses[month_key] = expense.amount

    all_months = sorted(
        set(monthly_income.keys())
        | set(monthly_expenses.keys())
    )

    monthly_income_labels = all_months

    monthly_income_values = [
        monthly_income.get(month, 0)
        for month in all_months
    ]

    monthly_expense_values = [
        monthly_expenses.get(month, 0)
        for month in all_months
    ]

    return render_template(
        "reports.html",
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,
        transaction_count=transaction_count,
        category_labels=category_labels,
        category_values=category_values,
        monthly_income_labels=monthly_income_labels,
        monthly_income_values=monthly_income_values,
        monthly_expense_values=monthly_expense_values
    )
    # --------------------------------------------------------
    # Current user's budget
    # --------------------------------------------------------

    budget_record = Budget.query.filter_by(

        user_id=current_user.id,

        month=current_month,

        year=current_year

    ).first()


    # ========================================================
    # SAVE BUDGET
    # ========================================================

    if request.method == "POST":

        amount_text = request.form.get(

            "amount",

            ""

        ).strip()


        if not amount_text:

            return "Please enter a budget amount."


        try:

            amount = float(
                amount_text
            )


            if amount <= 0:

                return (
                    "Budget must be greater than 0."
                )


        except ValueError:

            return (
                "Please enter a valid number."
            )


        if budget_record:

            budget_record.amount = amount


        else:

            budget_record = Budget(

                amount=amount,

                month=current_month,

                year=current_year,

                user_id=current_user.id

            )


            db.session.add(
                budget_record
            )


        db.session.commit()

        flash(
            "Budget saved successfully.",
            "success"
        )


        return redirect(
            url_for("budget")
        )


    # ========================================================
    # MONTHLY EXPENSES
    # ========================================================

    expenses = Expense.query.filter_by(

        user_id=current_user.id

    ).all()


    monthly_expenses = sum(

        expense.amount

        for expense in expenses

        if expense.date.month == current_month

        and expense.date.year == current_year

    )


    # ========================================================
    # MONTHLY BUDGET
    # ========================================================

    if budget_record:

        monthly_budget = budget_record.amount

    else:

        monthly_budget = 0


    # ========================================================
    # REMAINING BUDGET
    # ========================================================

    budget_remaining = (

        monthly_budget

        - monthly_expenses

    )


    # ========================================================
    # BUDGET PERCENTAGE
    # ========================================================

    if monthly_budget > 0:

        budget_percentage = (

            monthly_expenses

            / monthly_budget

        ) * 100

    else:

        budget_percentage = 0


    display_percentage = min(

        budget_percentage,

        100

    )


    month_name = date.today().strftime(
        "%B"
    )


    return render_template(

        "budget.html",

        monthly_budget=monthly_budget,

        monthly_expenses=monthly_expenses,

        budget_remaining=budget_remaining,

        budget_percentage=budget_percentage,

        display_percentage=display_percentage,

        month_name=month_name,

        current_year=current_year

    )


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

with app.app_context():

    update_existing_database()


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(debug=True)