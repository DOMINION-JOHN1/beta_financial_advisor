import os
import json
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.runnables import RunnableParallel

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="llama3-8b-8192",
    api_key=api_key,
    temperature=0.1,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

import pandas as pd
from io import StringIO

def parse_csv_content(content):
    # Split the content by double newlines to separate sections
    sections = content.split('\n\n')
    data_rows = []
    
    # Skip the first section (introductory text) and process the rest
    for section in sections[1:]:
        lines = section.strip().split('\n')
        if lines:
            # Skip the header line (e.g., "Income,Source,Amount")
            for line in lines[1:]:
                data_rows.append(line)
    
    # Join data rows into a single CSV string
    csv_string = '\n'.join(data_rows)
    
    # Read into a DataFrame with custom column names
    df = pd.read_csv(StringIO(csv_string), header=None, names=['Type', 'Field', 'Amount'])
    return df

def financial_planner(user_input: str) -> tuple:
    # Initialize Groq LLM
    llm = ChatGroq(
        model_name="llama3-8b-8192",
        temperature=0,
        max_tokens=1024
    )

    # CSV Budget Generator
    csv_prompt = PromptTemplate(
        template="""Convert this financial information into a CSV format:
        
        INCOME:
        - List all income sources with amounts
        EXPENSES:
        - Categorize expenses with amounts
        SAVINGS:
        - Calculate suggested savings
        
        Input: {user_input}
        
        Format exactly like this:
        Category,Item,Amount
        Income,[source],[amount]
        Expense,[category],[amount]
        Savings,[type],[amount]
        
        Use only numbers (no currency symbols) and simple categories.""",
        input_variables=["user_input"]
    )

    # Financial Advice Generator
    advice_prompt = PromptTemplate(
        template="""Provide concise financial advice for this situation:
        {user_input}
        
        Focus on:
        - Budget optimization
        - Emergency funds
        - Debt management
        - Long-term savings
        Use bullet points.""",
        input_variables=["user_input"]
    )

    # Create parallel chains
 
    
    chain = RunnableParallel(
        csv=csv_prompt | llm,
        advice=advice_prompt | llm
    )
    # Run both chains in parallel
    result = chain.invoke({"user_input": user_input})
    
    return result["csv"].content, result["advice"].content

# Example usage
if __name__ == "__main__":
    input_text = "Monthly income $5000. Rent $1200, groceries $400, utilities $200. Student loan $300. Want to save for vacation."
    
    csv_output, advice = financial_planner(input_text)
    
    df = parse_csv_content(csv_output)
    # Display the DataFrame
    print("=== BUDGET CSV ===")
    print(df)
    print("\n=== FINANCIAL ADVICE ===")
    print(advice)