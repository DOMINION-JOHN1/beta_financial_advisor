from dotenv import load_dotenv

from src.langchain_pipeline import run_budget_pipeline
from src.spreadsheet_generator import generate_budget_spreadsheet

load_dotenv()

# Example usage 2
if __name__ == "__main__":
    input_text = "Monthly income $5000. Rent $1200, groceries $400, utilities $200, Student loan $300. Want to save for vacation."

    result_data = run_budget_pipeline(input_text)

    print("=== INCOME ===\n")
    print(result_data["income"].content)
    print("=== EXPENSES ===\n")
    print(result_data["expenses"].content)
    print("=== ADVICE ===\n")
    advice_text = result_data["advice"].content
    print(advice_text)

    # Generate spreadsheet
    file_path = generate_budget_spreadsheet(result_data)

    print("=== FILE PATH ===\n")
    print(file_path)
