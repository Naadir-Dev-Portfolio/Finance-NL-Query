# financial_functions.py

import pandas as pd
from datetime import datetime, timedelta

def get_current_balance(df):
    """Returns the current balance from the DataFrame."""
    return df['Balance'].iloc[-1]

def calculate_total_income(df, start_date=None, end_date=None):
    """Calculates the total income from the DataFrame within an optional date range."""
    if not start_date:
        start_date = df['Date'].min()
    if not end_date:
        end_date = df['Date'].max()
    mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
    return df.loc[mask, 'Paid in'].sum()

def calculate_total_expenses(df, start_date=None, end_date=None):
    """Calculates the total expenses from the DataFrame within an optional date range."""
    if not start_date:
        start_date = df['Date'].min()
    if not end_date:
        end_date = df['Date'].max()
    mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
    return df.loc[mask, 'Paid out'].sum()

def get_top_expense_categories(df, start_date=None, end_date=None):
    """Returns the top 5 expense categories from the DataFrame within an optional date range."""
    if not start_date:
        start_date = df['Date'].min()
    if not end_date:
        end_date = df['Date'].max()
    mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
    filtered_df = df.loc[mask]
    return filtered_df.groupby('Transaction type')['Paid out'].sum().sort_values(ascending=False).head(5)

def calculate_spending_by_store(df, store_name, start_date=None, end_date=None):
    """Calculates total spending at a particular store within an optional date range."""
    if not start_date:
        start_date = df['Date'].min()
    if not end_date:
        end_date = df['Date'].max()
    mask = (df['Description'].str.contains(store_name, case=False, na=False)) & (df['Date'] >= start_date) & (df['Date'] <= end_date)
    return df.loc[mask, 'Paid out'].sum()

def calculate_spending_by_transaction_type(df, transaction_type, start_date=None, end_date=None):
    """Calculates total spending for a particular transaction type within an optional date range."""
    if not start_date:
        start_date = df['Date'].min()
    if not end_date:
        end_date = df['Date'].max()
    mask = (df['Transaction type'].str.contains(transaction_type, case=False, na=False)) & (df['Date'] >= start_date) & (df['Date'] <= end_date)
    return df.loc[mask, 'Paid out'].sum()

# Add more functions as needed...
