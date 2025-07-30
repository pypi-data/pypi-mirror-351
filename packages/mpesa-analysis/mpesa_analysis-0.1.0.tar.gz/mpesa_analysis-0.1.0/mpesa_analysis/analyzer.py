# mpesa_analysis/mpesa_analysis/analyzer.py
import pandas as pd
import pdfplumber
import numpy as np
import os # For checking file existence

def extract_table_from_pdf(pdf_path: str, password: str, target_header: str) -> pd.DataFrame:
    """
    Extracts a specific table from a password-protected PDF.

    Args:
        pdf_path (str): Path to the PDF file.
        password (str): Password for the PDF file.
        target_header (str): The expected header row (comma-separated string) to identify the table.

    Returns:
        pd.DataFrame: A DataFrame containing the extracted table data.

    Raises:
        ValueError: If the target table or data is not found in the PDF.
        Exception: For any other errors during PDF processing.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

    try:
        # Use a context manager to ensure the PDF file is closed
        with pdfplumber.open(pdf_path, password=password) as pdf:
            data = []
            found = False
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if table and ",".join([str(i).strip() for i in table[0]]) == target_header:
                        found = True
                        data.extend(table)
                    elif found and table and len(table[0]) == len(target_header.split(',')): # Basic check for consistent column count
                         data.extend(table)
            if not found:
                raise ValueError(f"Target table with header '{target_header}' not found in the PDF.")
            
            if len(data) <= 1:
                raise ValueError("No data rows found after the header in the target table.")
                
            # Ensure columns from header are valid for DataFrame
            columns = [col.strip() for col in data[0]]
            # Ensure data rows match column count
            valid_data_rows = [row for row in data[1:] if row is not None and len(row) == len(columns)]
            
            return pd.DataFrame(valid_data_rows, columns=columns)
    except Exception as e:
        raise Exception(f"Failed to extract table from PDF: {e}")

def categorize_mpesa_transaction(detail: str, amount: float) -> str:
    """
    Categorizes a single M-Pesa transaction based on its details and amount.

    Args:
        detail (str): The 'Details' string from the M-Pesa statement.
        amount (float): The 'Amount' (Paid In - Withdrawn) of the transaction.

    Returns:
        str: The categorized type of transaction (e.g., "Income", "Loan_Repayment", "Purchase").
    """
    if pd.isna(detail): return "Unknown"
    d = detail.lower()

    if amount > 0:
        if "received from" in d or "funds received" in d or "pay bill" in d or "deposit" in d:
            return "Income"
        return "Other_Income"

    if amount < 0:
        if "fuliza" in d or "overdraft" in d or ("loan" in d and ("taken" in d or "disbursed" in d)):
            return "Loan_Taken"
        if "loan repayment" in d or ("m-shwari" in d and "loan" in d and "repayment" in d):
            return "Loan_Repayment"
        if "buy" in d or "payment" in d or "paid to" in d:
            return "Purchase"
        if "sent to" in d or "transfer" in d:
            return "Transfer_Out"
        if "withdraw" in d or "cash out" in d:
            return "Cash_Withdrawal"
        if "airtime" in d or "data" in d:
            return "Airtime_Data"
        if "bank" in d and "transfer" in d:
            return "Bank_Transfer_Out"
        return "Other_Expense"

    return "Zero_Transaction"

def analyze_mpesa_statement(pdf_path: str, password: str) -> dict:
    """
    Analyzes an M-Pesa PDF statement to derive core financial metrics.

    Args:
        pdf_path (str): Path to the M-Pesa PDF file.
        password (str): Password for the PDF file.

    Returns:
        dict: A dictionary containing calculated financial metrics:
              'avg_monthly_income', 'avg_monthly_expenses', 'avg_existing_emis',
              'avg_net_cash_flow', 'avg_loan_to_income_ratio', 'is_high_risk'.
              Returns default zeros/False if analysis fails.
    """
    header = "Receipt No.,Completion Time,Details,Transaction Status,Paid In,Withdrawn,Balance"
    try:
        df = extract_table_from_pdf(pdf_path, password, header)
    except Exception as e:
        print(f"Error during PDF extraction: {e}")
        return {
            'avg_monthly_income': 0, 'avg_monthly_expenses': 0, 'avg_existing_emis': 0,
            'avg_net_cash_flow': 0, 'avg_loan_to_income_ratio': 0, 'is_high_risk': True
        }

    # Clean and convert data types
    df["Paid In"] = pd.to_numeric(df["Paid In"], errors="coerce").fillna(0)
    df["Withdrawn"] = pd.to_numeric(df["Withdrawn"], errors="coerce").fillna(0)
    df["Amount"] = df["Paid In"] - df["Withdrawn"]
    df["Completion Time"] = pd.to_datetime(df["Completion Time"], errors="coerce")
    df = df.dropna(subset=['Completion Time']) # Drop rows where date parsing failed
    
    if df.empty:
        print("DataFrame is empty after cleaning. No data to analyze.")
        return {
            'avg_monthly_income': 0, 'avg_monthly_expenses': 0, 'avg_existing_emis': 0,
            'avg_net_cash_flow': 0, 'avg_loan_to_income_ratio': 0, 'is_high_risk': True
        }

    df["YearMonth"] = df["Completion Time"].dt.to_period("M")

    # Apply categorization
    df["Category"] = df.apply(lambda row: categorize_mpesa_transaction(row["Details"], row["Amount"]), axis=1)

    # Group by month and category for detailed summary
    summary_by_month = df.groupby(["YearMonth", "Category"])["Amount"].sum().unstack(fill_value=0)

    # Calculate overall monthly averages
    avg_monthly_income = (summary_by_month["Income"].mean() if "Income" in summary_by_month.columns else 0) + \
                         (summary_by_month["Other_Income"].mean() if "Other_Income" in summary_by_month.columns else 0)

    expense_categories = [col for col in summary_by_month.columns if col in ['Purchase', 'Transfer_Out',
                                                                            'Cash_Withdrawal', 'Airtime_Data',
                                                                            'Bank_Transfer_Out', 'Other_Expense']]
    avg_monthly_expenses = summary_by_month[expense_categories].abs().sum(axis=1).mean() if expense_categories else 0

    avg_existing_emis = summary_by_month["Loan_Repayment"].abs().mean() if "Loan_Repayment" in summary_by_month.columns else 0

    avg_net_cash_flow = avg_monthly_income - avg_monthly_expenses - avg_existing_emis

    avg_loan_to_income_ratio = (avg_existing_emis / avg_monthly_income) if avg_monthly_income > 0 else 0
    if not np.isfinite(avg_loan_to_income_ratio):
        avg_loan_to_income_ratio = 0

    is_high_risk = bool(avg_net_cash_flow < 0 or avg_loan_to_income_ratio > 0.5)

    return {
        'avg_monthly_income': round(avg_monthly_income, 2),
        'avg_monthly_expenses': round(avg_monthly_expenses, 2),
        'avg_existing_emis': round(avg_existing_emis, 2),
        'avg_net_cash_flow': round(avg_net_cash_flow, 2),
        'avg_loan_to_income_ratio': round(avg_loan_to_income_ratio, 2),
        'is_high_risk': is_high_risk
    }