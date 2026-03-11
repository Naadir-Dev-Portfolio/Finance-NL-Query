# main.py

import sys
import re
import pandas as pd
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QTextEdit, QLineEdit, QWidget
from sentence_transformers import SentenceTransformer, util
from financial_functions import (  # Import functions from financial_functions.py
    get_current_balance,
    calculate_total_income,
    calculate_total_expenses,
    get_top_expense_categories,
    calculate_spending_by_store,
    calculate_spending_by_transaction_type,
)

class QueryMatcher:
    def __init__(self):
        # Load a sentence transformer model
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        
        # Define query templates and corresponding functions
        self.query_templates = {
            "current balance": get_current_balance,
            "total income": calculate_total_income,
            "total expenses": calculate_total_expenses,
            "top expense categories": get_top_expense_categories,
            "spending by store": calculate_spending_by_store,
            "spending by transaction type": calculate_spending_by_transaction_type,
            # Add more templates and functions here...
        }
        
        # Encode the query templates
        self.template_embeddings = self.model.encode(list(self.query_templates.keys()), convert_to_tensor=True)
    
    def match_query_to_function(self, user_query):
        """Matches a user query to the closest predefined function."""
        # Encode the user query
        query_embedding = self.model.encode(user_query, convert_to_tensor=True)
        
        # Find the closest matching template
        cos_sim = util.pytorch_cos_sim(query_embedding, self.template_embeddings)
        best_match_idx = cos_sim.argmax().item()
        
        # Retrieve the corresponding function and template
        matched_function = list(self.query_templates.values())[best_match_idx]
        matched_template = list(self.query_templates.keys())[best_match_idx]
        return matched_function, matched_template

    def extract_dates_from_query(self, query):
        """Extracts start and end dates from a user query using regex."""
        date_pattern = r'\b(\d{4}-\d{2}-\d{2})\b'
        dates = re.findall(date_pattern, query)
        if len(dates) == 2:
            return pd.to_datetime(dates[0]), pd.to_datetime(dates[1])
        elif len(dates) == 1:
            return pd.to_datetime(dates[0]), None
        else:
            return None, None


class FinancialAdvisorApp(QMainWindow):
    def __init__(self, df):
        super().__init__()
        self.df = df
        self.query_matcher = QueryMatcher()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("AI Financial Advisor")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Text area to display AI responses
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

        # Input area for user queries
        self.input_area = QLineEdit()
        self.input_area.setPlaceholderText("Ask about your finances...")
        self.input_area.returnPressed.connect(self.on_enter_pressed)
        layout.addWidget(self.input_area)

    def on_enter_pressed(self):
        query = self.input_area.text().lower()

        # Extract start and end dates from the query
        start_date, end_date = self.query_matcher.extract_dates_from_query(query)

        matched_function, matched_template = self.query_matcher.match_query_to_function(query)

        # Determine how to call the matched function
        if matched_template in ["current balance"]:
            # Functions that don't require dates
            result = matched_function(self.df)
        elif matched_template == "spending by store":
            # Example: "How much did I spend at Starbucks?"
            store_name = query.split(' at ')[-1]
            result = matched_function(self.df, store_name, start_date, end_date)
        elif matched_template == "spending by transaction type":
            transaction_type = query.split(' on ')[-1]
            result = matched_function(self.df, transaction_type, start_date, end_date)
        else:
            # Functions that do require dates
            result = matched_function(self.df, start_date, end_date)
        
        # Generate a natural language response
        response = self.construct_response(query, result)
        self.output_area.append(response)
        self.input_area.clear()

    def construct_response(self, query, result):
        """Constructs a natural language response based on the query and result."""
        if "spend" in query or "spent" in query:
            return f"You spent {result:.2f} for the queried period."
        elif "earn" in query or "income" in query:
            return f"You earned {result:.2f} for the queried period."
        elif "balance" in query:
            return f"Your current balance is {result:.2f}."
        else:
            return f"The result for your query '{query}' is: {result:.2f}"

# The main function to run the application
def main():
    # Load your financial data
    df = pd.read_csv(r"D:\Libraries\Documents\Echo Sphere One\Main\gui\data_processing\Inspect\cleansed_financial_data.csv")
    df['Date'] = pd.to_datetime(df['Date'])  # Ensure the Date column is in datetime format
    
    # Initialize the PyQt6 application
    app = QApplication(sys.argv)
    advisor_app = FinancialAdvisorApp(df)
    advisor_app.show()
    
    # Execute the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
