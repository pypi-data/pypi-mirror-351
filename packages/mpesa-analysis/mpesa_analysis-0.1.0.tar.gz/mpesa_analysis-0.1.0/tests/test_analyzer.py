# mpesa_analysis/tests/test_analyzer.py
import pytest
import pandas as pd
import numpy as np
import os
from unittest.mock import patch, mock_open

# Assume analyzer.py is in the parent directory of tests.
# For a proper package install, it will be found via 'mpesa_analysis.'
from mpesa_analysis.analyzer import extract_table_from_pdf, categorize_mpesa_transaction, analyze_mpesa_statement

# Fixture to create a dummy PDF file path (not a valid PDF content for extraction)
# For actual extraction tests, you would need a small, valid, dummy M-Pesa PDF.
@pytest.fixture
def dummy_pdf_path(tmp_path):
    # This creates an empty file. pdfplumber will likely fail to open it as a valid PDF.
    # For robust testing, you'd generate a real minimal PDF or mock pdfplumber's internals.
    path = tmp_path / "test_statement.pdf"
    path.write_bytes(b"%PDF-1.4\n1 0 obj <</Type/Catalog/Pages 2 0 R>> endobj\n2 0 obj <</Type/Pages/Count 0>> endobj\nxref\n0 3\n0000000000 65535 f\n0000000009 00000 n\n0000000055 00000 n\ntrailer\n<</Size 3/Root 1 0 R>>\nstartxref\n106\n%%EOF")
    return str(path)

# Mock data for extract_table_from_pdf to simulate a valid PDF table
@pytest.fixture
def mock_pdf_table_data():
    return [
        ["Receipt No.", "Completion Time", "Details", "Transaction Status", "Paid In", "Withdrawn", "Balance"],
        ["ABCD1", "2024-01-15 10:00:00", "Received from JOHN DOE", "Completed", "10000", "", "15000"],
        ["ABCD2", "2024-01-16 11:00:00", "Payment to Safaricom", "Completed", "", "2000", "13000"],
        ["ABCD3", "2024-01-17 12:00:00", "Loan repayment to M-Shwari", "Completed", "", "1500", "11500"],
        ["ABCD4", "2024-02-01 09:00:00", "Loan disbursed from Tala", "Completed", "5000", "", "16500"],
        ["ABCD5", "2024-02-02 10:00:00", "Sent to JANE DOE", "Completed", "", "1000", "15500"],
    ]

# Test extract_table_from_pdf with a mock
def test_extract_table_from_pdf_with_mock(dummy_pdf_path, mock_pdf_table_data):
    # Patch pdfplumber.open to return a mock PDF object
    with patch('pdfplumber.open') as mock_plumber_open:
        mock_pdf = mock_plumber_open.return_value.__enter__.return_value # Mock the opened PDF context manager
        mock_page = mock_pdf.pages[0] # Access the first page
        mock_page.extract_tables.return_value = [mock_pdf_table_data]

        header = "Receipt No.,Completion Time,Details,Transaction Status,Paid In,Withdrawn,Balance"
        df = extract_table_from_pdf(dummy_pdf_path, "any_password", header)

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert list(df.columns) == header.split(',')
        assert len(df) == 5 # 5 data rows

def test_extract_table_from_pdf_not_found(dummy_pdf_path):
    with patch('pdfplumber.open') as mock_plumber_open:
        mock_pdf = mock_plumber_open.return_value.__enter__.return_value
        mock_pdf.pages[0].extract_tables.return_value = [] # No tables found

        with pytest.raises(ValueError, match="Target table with header 'NonExistent' not found"):
            extract_table_from_pdf(dummy_pdf_path, "pass", "NonExistent")

def test_categorize_mpesa_transaction():
    assert categorize_mpesa_transaction("Received from JOHN DOE", 1000) == "Income"
    assert categorize_mpesa_transaction("Pay Bill for KPLC", -500) == "Purchase"
    assert categorize_mpesa_transaction("Loan repayment to M-Shwari", -200) == "Loan_Repayment"
    assert categorize_mpesa_transaction("Loan disbursed from Tala", 5000) == "Income" # Loan received is income for cash flow
    assert categorize_mpesa_transaction("Fuliza loan taken", -1000) == "Loan_Taken"
    assert categorize_mpesa_transaction("Withdrawal from Agent 12345", -2000) == "Cash_Withdrawal"
    assert categorize_mpesa_transaction("Sent to JANE DOE", -300) == "Transfer_Out"
    assert categorize_mpesa_transaction("Airtime Purchase", -50) == "Airtime_Data"
    assert categorize_mpesa_transaction("Bank Transfer out", -1500) == "Bank_Transfer_Out"
    assert categorize_mpesa_transaction(np.nan, 0) == "Unknown"
    assert categorize_mpesa_transaction("Some other transaction", 0) == "Zero_Transaction"


def test_analyze_mpesa_statement_success(dummy_pdf_path, mock_pdf_table_data):
    with patch('pdfplumber.open') as mock_plumber_open:
        mock_pdf = mock_plumber_open.return_value.__enter__.return_value
        mock_page = mock_pdf.pages[0]
        mock_page.extract_tables.return_value = [mock_pdf_table_data]

        results = analyze_mpesa_statement(dummy_pdf_path, "any_password")

        assert isinstance(results, dict)
        assert 'avg_monthly_income' in results
        assert 'avg_monthly_expenses' in results
        assert 'avg_existing_emis' in results
        assert 'is_high_risk' in results

        # Based on mock_pdf_table_data for Jan & Feb:
        # Jan: Income 10000, Expenses 2000 (Purchase), EMIs 1500
        # Feb: Income 5000 (Loan Disbursed), Expenses 1000 (Transfer_Out)
        # Avg Income: (10000 + 5000) / 2 = 7500
        # Avg Expenses (Purchase, Transfer_Out, Cash_Withdrawal, Airtime_Data, Bank_Transfer_Out, Other_Expense): (2000 + 1000) / 2 = 1500
        # Avg Existing EMIs: 1500 / 2 = 750 (since only one month had repayment)
        # These are simple averages across months present in data.
        
        # Note: The 'Loan disbursed from Tala' is treated as income for cash flow purposes here,
        # but in a more detailed financial analysis, you might want to differentiate it.
        # This test relies on the categorization logic in analyzer.py.
        
        # Adjust expected values based on average calculations
        expected_avg_income = (10000 + 5000) / 2 # Income + Loan_Taken
        expected_avg_expenses = (2000 + 1000) / 2 # Purchase + Transfer_Out
        expected_avg_emis = 1500 / 2 # Only one month had loan repayment
        
        # Allow for floating point precision
        assert results['avg_monthly_income'] == pytest.approx(expected_avg_income)
        assert results['avg_monthly_expenses'] == pytest.approx(expected_avg_expenses)
        assert results['avg_existing_emis'] == pytest.approx(expected_avg_emis)
        assert results['avg_net_cash_flow'] == pytest.approx(expected_avg_income - expected_avg_expenses - expected_avg_emis)

def test_analyze_mpesa_statement_empty_df(dummy_pdf_path):
    with patch('pdfplumber.open') as mock_plumber_open:
        mock_pdf = mock_plumber_open.return_value.__enter__.return_value
        mock_page = mock_pdf.pages[0]
        mock_page.extract_tables.return_value = [
            ["Receipt No.", "Completion Time", "Details", "Transaction Status", "Paid In", "Withdrawn", "Balance"]
        ] # Header, but no data rows

        results = analyze_mpesa_statement(dummy_pdf_path, "any_password")
        assert results['avg_monthly_income'] == 0
        assert results['avg_monthly_expenses'] == 0
        assert results['is_high_risk'] == True # Default high risk if no data