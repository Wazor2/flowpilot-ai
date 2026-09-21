import sqlite3
import pandas as pd
import os
from reportlab.pdfgen import canvas

def create_database():
    conn = sqlite3.connect('invoices.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            invoice_id TEXT PRIMARY KEY,
            customer_name TEXT,
            email TEXT,
            amount REAL,
            due_date TEXT,
            status TEXT
        )
    ''')
    
    invoices_data = [
        # Account A: Overdue > $1,000, valid email
        ('INV-001', 'Acme Corp', 'billing@acmecorp.com', 1500.00, '2023-10-01', 'OVERDUE'),
        # Account B: Overdue, missing email in DB
        ('INV-002', 'Globex Inc', None, 800.00, '2023-10-05', 'OVERDUE'),
        # Account C: Listed overdue in DB, but has a matching payment entry in bank_statements.csv
        ('INV-003', 'Initech', 'finance@initech.com', 500.00, '2023-10-10', 'OVERDUE'),
        # Regular paid invoice
        ('INV-004', 'Stark Industries', 'accounts@stark.com', 2000.00, '2023-09-15', 'PAID')
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO invoices (invoice_id, customer_name, email, amount, due_date, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', invoices_data)
    
    conn.commit()
    conn.close()
    print("Created invoices.db")

def create_bank_statements():
    data = {
        'transaction_id': ['TXN-101', 'TXN-102', 'TXN-103'],
        'date': ['2023-10-11', '2023-10-12', '2023-10-13'],
        'description': ['Payment from Stark Industries', 'Wire Transfer Initech INV-003', 'Monthly Fee'],
        'amount': [2000.00, 500.00, -15.00]
    }
    df = pd.DataFrame(data)
    df.to_csv('bank_statements.csv', index=False)
    print("Created bank_statements.csv")

def create_pdf_notes():
    # Adjusted path since this will be run from the 'data' directory or project root
    # Creating customer_notes inside data/
    os.makedirs('customer_notes', exist_ok=True)
    
    # Create a PDF for Globex Inc (missing email in DB)
    pdf_path = os.path.join('customer_notes', 'Globex_Inc_Notes.pdf')
    c = canvas.Canvas(pdf_path)
    c.drawString(100, 750, "Customer CRM Notes: Globex Inc")
    c.drawString(100, 730, "Contact Name: Hank Scorpio")
    c.drawString(100, 710, "Email: hank@globex.com")
    c.drawString(100, 690, "Phone: 555-0199")
    c.drawString(100, 670, "Notes: Customer prefers email communication for overdue notices.")
    c.save()
    print(f"Created {pdf_path}")

if __name__ == '__main__':
    create_database()
    create_bank_statements()
    create_pdf_notes()
