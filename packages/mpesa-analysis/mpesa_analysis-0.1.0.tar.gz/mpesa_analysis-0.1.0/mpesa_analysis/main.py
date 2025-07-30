# mpesa_analysis/mpesa_analysis/main.py
import os
from flask import Flask, request, jsonify, render_template
import tempfile
import shutil
import pandas as pd # Used for to_dict(orient='records')
from dotenv import load_dotenv # Import to load .env file

# Load environment variables from .env file
load_dotenv()

# Import your core logic from the package
from .analyzer import analyze_mpesa_statement
from .recommender import generate_financial_summary_for_gemini, get_gemini_loan_recommendation

app = Flask(__name__)

@app.route('/')
def index():
    """Renders the HTML form for PDF upload."""
    return render_template('index.html')

@app.route('/upload_and_advise', methods=['POST'])
def upload_and_advise():
    """Handles PDF upload, processes it, and returns Gemini's advice."""
    if 'pdf_file' not in request.files:
        return jsonify({"error": "No PDF file part in the request"}), 400
    if 'password' not in request.form: # Use 'in request.form' for form data
        return jsonify({"error": "No password provided"}), 400
    if 'credit_score' not in request.form:
        return jsonify({"error": "No credit score provided"}), 400

    pdf_file = request.files['pdf_file']
    password = request.form['password']
    
    try:
        borrower_credit_score = int(request.form['credit_score'])
        if not (300 <= borrower_credit_score <= 850):
            return jsonify({"error": "Credit score must be between 300 and 850."}), 400
    except ValueError:
        return jsonify({"error": "Invalid credit score provided. Must be a number."}), 400

    if pdf_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    temp_dir = None
    try:
        # Create a temporary directory to save the uploaded file
        temp_dir = tempfile.mkdtemp()
        filepath = os.path.join(temp_dir, pdf_file.filename)
        pdf_file.save(filepath)

        print(f"Uploaded PDF saved to: {filepath}")

        # Step 1: Analyze M-Pesa statement
        print("Analyzing M-Pesa statement...")
        analysis_results = analyze_mpesa_statement(filepath, password)

        if analysis_results['avg_monthly_income'] == 0 and analysis_results['avg_monthly_expenses'] == 0:
            return jsonify({
                "error": "Failed to derive meaningful financial data from PDF. Please check the file and password.",
                "details": "Income and expenses are zero, indicating no data was extracted or parsed correctly."
            }), 400

        # Step 2: Prepare the summary DataFrame for Gemini
        summary_df_for_gemini = generate_financial_summary_for_gemini(analysis_results, borrower_credit_score)
        print("\n--- Financial Summary for Gemini Model ---")
        print(summary_df_for_gemini)

        # Step 3: Get loan recommendations from Gemini
        print("\nRequesting loan recommendations from Gemini AI...")
        gemini_recommendations = get_gemini_loan_recommendation(summary_df_for_gemini)

        return jsonify({
            "status": "success",
            "analysis_from_pdf": analysis_results,
            "summary_for_gemini": summary_df_for_gemini.to_dict(orient='records'),
            "gemini_advice": gemini_recommendations
        }), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": f"An error occurred during processing: {str(e)}"}), 500
    finally:
        # Clean up the temporary directory and its contents
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temporary directory: {temp_dir}")

if __name__ == '__main__':
    # Ensure templates directory exists for Flask
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Check if GEMINI_API_KEY is set (for direct run)
    if "GEMINI_API_KEY" not in os.environ:
        print("WARNING: GEMINI_API_KEY environment variable is not set.")
        print("Please set it in your .env file or environment for Gemini integration to work.")
        print("e.g., create a .env file in the root directory with: GEMINI_API_KEY=YOUR_API_KEY")
    
    app.run(debug=True, port=5000)