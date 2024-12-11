"""
Author: Zohaib Tunio
Date Written: 
Asssignment: Final Project
Short Desc: This Finance Tracker app lets you add Income, Expense and displays the Total budget remaining. 
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# Database setup
def setup_database():
    conn = sqlite3.connect("finance_tracker.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Fetch totals and recent transactions
def get_totals():
    conn = sqlite3.connect("finance_tracker.db")
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) FROM income")
    total_income = cursor.fetchone()[0] or 0.0

    cursor.execute("SELECT SUM(amount) FROM expenses")
    total_expenses = cursor.fetchone()[0] or 0.0

    balance = total_income - total_expenses

    conn.close()
    return total_income, total_expenses, balance


def get_recent_transactions():
    conn = sqlite3.connect("finance_tracker.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, source, amount, date FROM income ORDER BY date DESC LIMIT 5")
    recent_income = cursor.fetchall()

    cursor.execute("SELECT id, category, amount, date FROM expenses ORDER BY date DESC LIMIT 5")
    recent_expenses = cursor.fetchall()

    conn.close()
    return recent_income, recent_expenses

# Add income to database
def add_income(source, amount, date):
    conn = sqlite3.connect("finance_tracker.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO income (source, amount, date) VALUES (?, ?, ?)", (source, amount, date))
    conn.commit()
    conn.close()

# Remove income from database
def remove_income(income_id):
    conn = sqlite3.connect("finance_tracker.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM income WHERE id = ?", (income_id,))
    conn.commit()
    conn.close()

# Add expense to database
def add_expense(category, amount, date):
    conn = sqlite3.connect("finance_tracker.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (category, amount, date) VALUES (?, ?, ?)", (category, amount, date))
    conn.commit()
    conn.close()

# Remove expense from database
def remove_expense(expense_id):
    conn = sqlite3.connect("finance_tracker.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

# Main Application
class FinanceTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Tracker")
        self.root.geometry("800x600")

        # Tab control
        self.tab_control = ttk.Notebook(root)

        # Tabs
        self.dashboard_tab = ttk.Frame(self.tab_control)
        self.income_tab = ttk.Frame(self.tab_control)
        self.expenses_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.dashboard_tab, text="Dashboard")
        self.tab_control.add(self.income_tab, text="Income")
        self.tab_control.add(self.expenses_tab, text="Expenses")
        self.tab_control.pack(expand=1, fill="both")

        # Initialize tabs
        self.init_dashboard_tab()
        self.init_income_tab()
        self.init_expenses_tab()

    # Dashboard Tab
    def init_dashboard_tab(self):
        ttk.Label(self.dashboard_tab, text="Welcome to the Personal Finance Tracker!", font=("Arial", 16)).pack(pady=20)

        self.balance_label = ttk.Label(self.dashboard_tab, text="", font=("Arial", 14))
        self.balance_label.pack(pady=10)

        ttk.Label(self.dashboard_tab, text="Recent Transactions:", font=("Arial", 14)).pack(pady=10)

        self.transactions_frame = ttk.Frame(self.dashboard_tab)
        self.transactions_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.update_dashboard()

    def update_dashboard(self):
        total_income, total_expenses, balance = get_totals()
        self.balance_label.config(text=f"Total Income: ${total_income:.2f} | Total Expenses: ${total_expenses:.2f} | Balance: ${balance:.2f}")

        for widget in self.transactions_frame.winfo_children():
            widget.destroy()

        recent_income, recent_expenses = get_recent_transactions()

        ttk.Label(self.transactions_frame, text="Recent Income:", font=("Arial", 12)).pack(anchor="w")
        for income in recent_income:
            ttk.Label(self.transactions_frame, text=f"{income[1]}: ${income[2]:.2f} on {income[3]}").pack(anchor="w")
            ttk.Button(self.transactions_frame, text="Remove", command=lambda id=income[0]: self.delete_income(id)).pack(anchor="w")

        ttk.Label(self.transactions_frame, text="Recent Expenses:", font=("Arial", 12)).pack(anchor="w", pady=(10, 0))
        for expense in recent_expenses:
            ttk.Label(self.transactions_frame, text=f"{expense[1]}: ${expense[2]:.2f} on {expense[3]}").pack(anchor="w")
            ttk.Button(self.transactions_frame, text="Remove", command=lambda id=expense[0]: self.delete_expense(id)).pack(anchor="w")

    def delete_income(self, income_id):
        remove_income(income_id)
        self.update_dashboard()

    def delete_expense(self, expense_id):
        remove_expense(expense_id)
        self.update_dashboard()

    # Income Tab
    def init_income_tab(self):
        ttk.Label(self.income_tab, text="Add Income", font=("Arial", 16)).pack(pady=10)

        # Input fields
        ttk.Label(self.income_tab, text="Source:").pack(anchor="w", padx=10, pady=5)
        self.income_source = ttk.Entry(self.income_tab)
        self.income_source.pack(fill="x", padx=10)

        ttk.Label(self.income_tab, text="Amount:").pack(anchor="w", padx=10, pady=5)
        self.income_amount = ttk.Entry(self.income_tab)
        self.income_amount.pack(fill="x", padx=10)

        ttk.Label(self.income_tab, text="Date (MM-DD-YYYY):").pack(anchor="w", padx=10, pady=5)
        self.income_date = ttk.Entry(self.income_tab)
        self.income_date.pack(fill="x", padx=10)

        ttk.Button(self.income_tab, text="Add Income", command=self.save_income).pack(pady=10)

    def save_income(self):
        source = self.income_source.get()
        amount = self.income_amount.get()
        date = self.income_date.get()

        if source and amount and date:
            try:
                # Convert and validate date format
                datetime.strptime(date, "%m-%d-%Y")
                add_income(source, float(amount), date)
                messagebox.showinfo("Success", "Income added successfully!")
                self.income_source.delete(0, tk.END)
                self.income_amount.delete(0, tk.END)
                self.income_date.delete(0, tk.END)
                self.update_dashboard()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount or date in MM-DD-YYYY format.")
        else:
            messagebox.showerror("Error", "All fields are required.")

    # Expenses Tab
    def init_expenses_tab(self):
        ttk.Label(self.expenses_tab, text="Add Expense", font=("Arial", 16)).pack(pady=10)

        # Input fields
        ttk.Label(self.expenses_tab, text="Category:").pack(anchor="w", padx=10, pady=5)
        self.expense_category = ttk.Combobox(self.expenses_tab, state="readonly")
        self.expense_category['values'] = [
            "Mortgage / Rent",
            "Utilities",
            "Car Gas",
            "Car Insurance",
            "Car Payment",
            "Phone",
            "Internet",
            "Shopping",
            "Entertainment",
            "Food and Eating Out",
            "Grocery"
        ]
        self.expense_category.pack(fill="x", padx=10)

        ttk.Label(self.expenses_tab, text="Amount:").pack(anchor="w", padx=10, pady=5)
        self.expense_amount = ttk.Entry(self.expenses_tab)
        self.expense_amount.pack(fill="x", padx=10)

        ttk.Label(self.expenses_tab, text="Date (MM-DD-YYYY):").pack(anchor="w", padx=10, pady=5)
        self.expense_date = ttk.Entry(self.expenses_tab)
        self.expense_date.pack(fill="x", padx=10)

        ttk.Button(self.expenses_tab, text="Add Expense", command=self.save_expense).pack(pady=10)

    def save_expense(self):
        category = self.expense_category.get()
        amount = self.expense_amount.get()
        date = self.expense_date.get()

        if category and amount and date:
            try:
                add_expense(category, float(amount), date)
                messagebox.showinfo("Success", "Expense added successfully!")
                self.expense_category.delete(0, tk.END)
                self.expense_amount.delete(0, tk.END)
                self.expense_date.delete(0, tk.END)
                self.update_dashboard()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount.")
        else:
            messagebox.showerror("Error", "All fields are required.")

# Main Execution
if __name__ == "__main__":
    setup_database()
    root = tk.Tk()
    app = FinanceTrackerApp(root)
    root.mainloop()
