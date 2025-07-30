# M-Pesa Loan Advisory System with Gemini AI

This project provides a web-based loan advisory system that analyzes a user's M-Pesa statement (PDF) to assess their financial behavior and recommends a suitable loan amount and payment period using Google's Gemini AI.

## Features

* **PDF Statement Analysis:** Extracts and categorizes M-Pesa transactions from a password-protected PDF.
* **Financial Metric Derivation:** Calculates key financial indicators like average monthly income, expenses, and existing loan repayments.
* **Gemini AI Integration:** Passes derived financial data to the Gemini Pro model for detailed financial behavior analysis and personalized loan recommendations (amount and tenure within 1 year).
* **Web Interface:** A simple Flask web application for users to upload their M-Pesa PDF and receive advice.
* **Modular Design:** Organized into distinct Python modules for better maintainability and testability.

## Directory Structure