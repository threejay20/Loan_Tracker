from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3

app = Flask(__name__)

# Database setup function to create tables for loans and payments
def init_db():
    conn = sqlite3.connect('loans.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loan_amount REAL NOT NULL,
            interest_rate REAL NOT NULL,
            start_date TEXT NOT NULL,
            payment_schedule TEXT NOT NULL,
            remaining_balance REAL NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loan_id INTEGER,
            payment_date TEXT NOT NULL,
            payment_amount REAL NOT NULL,
            FOREIGN KEY(loan_id) REFERENCES loans(id)
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database (create tables if they don't exist)
init_db()

# Home route - displays the list of loans and a form to add a new loan
@app.route('/')
def index():
    conn = sqlite3.connect('loans.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM loans")
    loans = cursor.fetchall()
    conn.close()
    return render_template('index.html', loans=loans)

# Route to add a new loan to the database
@app.route('/add_loan', methods=['POST'])
def add_loan():
    loan_amount = float(request.form['loan_amount'])
    interest_rate = float(request.form['interest_rate'])
    start_date = request.form['start_date']
    payment_schedule = request.form['payment_schedule']
    remaining_balance = loan_amount

    conn = sqlite3.connect('loans.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO loans (loan_amount, interest_rate, start_date, payment_schedule, remaining_balance)
        VALUES (?, ?, ?, ?, ?)
    ''', (loan_amount, interest_rate, start_date, payment_schedule, remaining_balance))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Route to add a payment to a loan and update the remaining balance
@app.route('/add_payment/<int:loan_id>', methods=['POST'])
def add_payment(loan_id):
    payment_amount = float(request.form['payment_amount'])
    payment_date = datetime.now().strftime("%Y-%m-%d")

    # Update remaining balance for the loan
    conn = sqlite3.connect('loans.db')
    cursor = conn.cursor()
    cursor.execute('SELECT remaining_balance FROM loans WHERE id = ?', (loan_id,))
    remaining_balance = cursor.fetchone()[0] - payment_amount
    cursor.execute('UPDATE loans SET remaining_balance = ? WHERE id = ?', (remaining_balance, loan_id))
    
    # Insert payment record into the payments table
    cursor.execute('INSERT INTO payments (loan_id, payment_date, payment_amount) VALUES (?, ?, ?)', 
                   (loan_id, payment_date, payment_amount))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

# New route to display payment history for a specific loan
@app.route('/payment_history/<int:loan_id>')
def payment_history(loan_id):
    conn = sqlite3.connect('loans.db')
    cursor = conn.cursor()
    
    # Fetch loan details
    cursor.execute('SELECT * FROM loans WHERE id = ?', (loan_id,))
    loan = cursor.fetchone()
    
    # Fetch all payments for the loan
    cursor.execute('SELECT * FROM payments WHERE loan_id = ?', (loan_id,))
    payments = cursor.fetchall()
    
    conn.close()
    
    return render_template('payment_history.html', loan=loan, payments=payments)

if __name__ == '__main__':
    app.run(debug=True)
