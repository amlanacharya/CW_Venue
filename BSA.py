import pandas as pd
import numpy as np

def clean_amount(amount_str):
    if isinstance(amount_str, str):
        return float(amount_str.replace('"', '').replace('=', '').replace(',', ''))
    return amount_str

def process_bank_statement(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        start_row = 0
        end_row = len(lines)
        for i, line in enumerate(lines):
            if 'Sl. No.' in line:
                start_row = i
            if 'Opening balance' in line:
                end_row = i
                break
        
        df = pd.read_csv(file_path, skiprows=start_row, nrows=end_row-start_row)
        df.columns = df.columns.str.strip()
        
        print("\n=== Initial DataFrame ===")
        print("DataFrame shape:", df.shape)
        print("\nColumns:", df.columns.tolist())
        print("\nSample data:")
        print(df.head())
        print("\nDataFrame Info:")
        df.info()
        
        df['Amount'] = df['Amount'].apply(clean_amount)
        df['Balance'] = df['Balance'].apply(clean_amount)
        
        income = df[df['Dr / Cr'] == 'CR'].copy()
        expenses = df[df['Dr / Cr'] == 'DR'].copy()
        
        print("\n=== Split DataFrames ===")
        print("\nIncome DataFrame shape:", income.shape)
        print("Income DataFrame Info:")
        income.info()
        
        print("\nExpenses DataFrame shape:", expenses.shape)
        print("Expenses DataFrame Info:")
        expenses.info()
        
        total_income = income['Amount'].sum()
        total_expenses = expenses['Amount'].sum()
        
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
        income['Date'] = pd.to_datetime(income['Date'], format='%d/%m/%Y', errors='coerce')
        expenses['Date'] = pd.to_datetime(expenses['Date'], format='%d/%m/%Y', errors='coerce')
        
        print("\n=== After Date Conversion ===")
        print("Date column dtype:", df['Date'].dtype)
        print("Sample dates:", df['Date'].head())
        print("Any NaT in dates:", df['Date'].isna().any())
        
        total_rows = len(df)
        income_rows = len(income)
        expenses_rows = len(expenses)
        
        df = df.dropna(subset=['Date'])
        income = income.dropna(subset=['Date'])
        expenses = expenses.dropna(subset=['Date'])
        
        dropped_rows = total_rows - len(df)
        dropped_income = income_rows - len(income)
        dropped_expenses = expenses_rows - len(expenses)
        
        if dropped_rows > 0:
            print("\n=== Data Quality Report ===")
            print(f"Total rows dropped: {dropped_rows}")
            print(f"Income entries dropped: {dropped_income}")
            print(f"Expense entries dropped: {dropped_expenses}")
            
        uc_income = income.sort_values('Date', ascending=False)
        uc_expenses = expenses.sort_values('Date', ascending=False)
        
        uc_income.to_csv('uc_income.csv', index=False)
        uc_expenses.to_csv('uc_expenses.csv', index=False)
        
        print("\n=== Financial Summary ===")
        print(f"Total Income: ₹{total_income:,.2f}")
        print(f"Total Expenses: ₹{total_expenses:,.2f}")
        print(f"Net Profit/Loss: ₹{total_income - total_expenses:,.2f}")
        
        df['Year_Month'] = df['Date'].dt.strftime('%B %Y')
        monthly_summary = []
        
        for month in sorted(df['Year_Month'].unique(), key=lambda x: pd.to_datetime(x, format='%B %Y')):
            month_data = df[df['Year_Month'] == month]
            month_income = month_data[month_data['Dr / Cr'] == 'CR']['Amount'].sum()
            month_expenses = month_data[month_data['Dr / Cr'] == 'DR']['Amount'].sum()
            net_amount = month_income - month_expenses
            profit_or_loss = "Profit" if net_amount >= 0 else "Loss"
            monthly_summary.append({
                'Month': month,
                'Income': month_income,
                'Expenses': month_expenses,
                'Net': net_amount
            })
        
        print("\n=== Monthly Summary ===")
        for month in monthly_summary:
            print(f"{month['Month']}:")
            print(f"  Income: ₹{month['Income']:,.2f}")
            print(f"  Expenses: ₹{month['Expenses']:,.2f}")
            print(f"  Net: ₹{abs(month['Net']):,.2f} ({'Profit' if month['Net'] >= 0 else 'Loss'})")
            print()

        return income, expenses, df
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return None, None, None

if __name__ == "__main__":
    file_path = 'Bank Statment last FY.csv'
    income_df, expenses_df, full_df = process_bank_statement(file_path)

