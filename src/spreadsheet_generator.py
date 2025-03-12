import os
import json

from datetime import datetime
import pandas as pd
from io import StringIO


def parse_csv_content(content):
    try:
        # Split the content by double newlines to separate sections
        sections = content.split("\n\n")
        data_rows = []

        # Skip the first section (introductory text) and process the rest
        for section in sections[1:]:
            lines = section.strip().split("\n")
            if lines:
                # Skip the header line (e.g., "Income,Source,Amount")
                for line in lines[1:]:
                    data_rows.append(line)

        # Join data rows into a single CSV string
        csv_string = "\n".join(data_rows)

        if len(csv_string) == 0:
            return None

        # Read into a DataFrame with custom column names
        df = pd.read_csv(
            StringIO(csv_string), header=None, names=["Type", "Field", "Amount"]
        )

        # File name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"generated_sheets/Budget_{timestamp}.csv"
        df.to_csv(file_path)
        return file_path
    except:
        print(f"Error while generating csv")
        return None


def parse_llm_response(response_content, data_type="list"):
    try:
        parsed_data = json.loads(response_content)
        return parsed_data
    except json.JSONDecodeError as e:
        print(f"Error parsing {data_type}: {e}")
        return [] if data_type == "list" else ""


def generate_budget_spreadsheet(data, output_dir="generated_sheets"):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Parse data
        income_data = parse_llm_response(
            data["income"].content, "income"
        )  # Assuming model returns list-like strings
        expenses_data = parse_llm_response(data["expenses"].content, "expenses")
        concerns_data = data["concerns"].content
        advice_text = data["advice"].content

        # DataFrames
        df_income = pd.DataFrame(income_data)
        df_expenses = pd.DataFrame(expenses_data)
        df_concerns = pd.DataFrame({"Goals/Concerns": [concerns_data]})
        df_advice = pd.DataFrame({"Advice": [advice_text]})

        # Calculate Net Savings
        total_income = sum([item["amount"] for item in income_data])
        total_expenses = sum([item["amount"] for item in expenses_data])
        net_savings = total_income - total_expenses

        summary = pd.DataFrame(
            {
                "Total Income": [total_income],
                "Total Expenses": [total_expenses],
                "Net Savings": [net_savings],
            }
        )

        # File name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"{output_dir}/Budget_{timestamp}.xlsx"

        # Write to Excel
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            summary.to_excel(writer, sheet_name="Summary", index=False)
            df_income.to_excel(writer, sheet_name="Income", index=False)
            df_expenses.to_excel(writer, sheet_name="Expenses", index=False)
            df_concerns.to_excel(writer, sheet_name="Goals_Concerns", index=False)
            df_advice.to_excel(writer, sheet_name="Advice", index=False)

        return file_path
    except:
        print(f"Error while generating spreadsheet")
        return None
