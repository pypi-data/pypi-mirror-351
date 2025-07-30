# mpesa_analysis/mpesa_analysis/recommender.py
import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv # Import to load .env file

# Load environment variables from .env file
load_dotenv()

def get_gemini_model():
    """Configures and returns the Gemini generative model."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Fallback to a placeholder for local testing if .env isn't used
        # In a deployed environment, this check should be more strict.
        if os.environ.get("FLASK_ENV") == "development": # Or check for DEBUG=True
            print("WARNING: GEMINI_API_KEY not found in environment variables. Using placeholder.")
            api_key = "YOUR_GEMINI_API_KEY_HERE_FROM_RECOOMENDER" # Placeholder for local testing if not set
        else:
            raise ValueError("GEMINI_API_KEY environment variable not set. Please set it to proceed.")
            
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash')

def generate_financial_summary_for_gemini(analysis_results: dict, credit_score: int) -> pd.DataFrame:
    """
    Creates a Pandas DataFrame in the format expected by the Gemini model.

    Args:
        analysis_results (dict): Dictionary from `analyzer.analyze_mpesa_statement`.
        credit_score (int): The borrower's credit score (obtained externally).

    Returns:
        pd.DataFrame: A DataFrame with 'Metric' and 'Value' columns.
    """
    return pd.DataFrame({
        'Metric': ['Monthly Income', 'Monthly Expenses', 'Existing EMIs', 'Credit Score'],
        'Value': [
            analysis_results['avg_monthly_income'],
            analysis_results['avg_monthly_expenses'],
            analysis_results['avg_existing_emis'],
            credit_score
        ]
    })

def get_gemini_loan_recommendation(summary_df_for_gemini: pd.DataFrame) -> str:
    """
    Sends the financial summary to the Gemini model and retrieves recommendations.

    Args:
        summary_df_for_gemini (pd.DataFrame): The DataFrame prepared for Gemini.

    Returns:
        str: The detailed financial behavior analysis and loan recommendations from Gemini.

    Raises:
        Exception: If there's an error calling the Gemini API.
    """
    model = get_gemini_model()
    df_string = summary_df_for_gemini.to_string(index=False)

    prompt = f"""
    Analyze the following financial summary for a potential loan applicant, derived from their M-Pesa statement and other assumptions (e.g., credit score provided by user).
    Based on this information, recommend a suitable loan amount and a payment period within one year (maximum 12 months).
    Also, provide a detailed assessment of their financial behavior and actionable suggestions for improvement.

    **Financial Summary:**
    {df_string}

    **Key areas to cover in your analysis and recommendations:**
    1.  **Affordability Assessment:**
        * Calculate and comment on their disposable income based on the provided data.
        * What is a safe maximum monthly EMI they can comfortably afford, considering their income, expenses, and existing financial commitments?
    2.  **Recommended Loan Details:**
        * **Recommended Loan Amount:** State a specific numerical amount (e.g., KES 150,000).
        * **Recommended Payment Period:** State a specific number of months (e.g., 6 months, 9 months, or 12 months - must be <= 12 months).
        * **Justification for Recommendation:** Explain why this specific amount and period are suitable, considering their financial health and risk.
        * **Estimated EMI for Recommended Loan:** Provide an estimate. **Assume an annual interest rate of 12% for short-term personal loans.**
    3.  **Financial Behavior Assessment:**
        * Overall assessment of their current financial standing based on income, expenses, existing debt, and credit score.
        * Identify strengths and weaknesses in their financial habits.
    4.  **Actionable Recommendations for Improvement:**
        * Strategies to optimize their budget and reduce unnecessary expenses.
        * Advice on managing their existing EMIs more effectively.
        * Steps to further improve their credit score (even if it's a placeholder, suggest general credit-building advice).
        * General advice for building a stronger financial foundation for future borrowing or savings.

    Provide the analysis and recommendations in a clear, structured, and professional manner, suitable for a financial advisor.
    Be precise with the recommended loan amount and payment period.
    """

    try:
        response = model.generate_content(prompt)
        if response:
            return response.text
        else:
            return "No response received from Gemini for the financial analysis."
    except Exception as e:
        raise Exception(f"An error occurred while calling the Gemini API: {e}")