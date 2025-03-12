from dotenv import load_dotenv

from src.langchain_pipeline import financial_planner
from src.spreadsheet_generator import parse_csv_content

load_dotenv()

# Example usage
if __name__ == "__main__":
    input_text = "I earn $4000 from my job and $500 freelancing. My rent is $1200, food costs $400, transport $300. I want to save for a house."

    csv_output, advice = financial_planner(input_text)

    df = parse_csv_content(csv_output)
    # Display the DataFrame
    print("=== BUDGET CSV ===")
    print(df)
    print("\n=== FINANCIAL ADVICE ===")
    print(advice)
