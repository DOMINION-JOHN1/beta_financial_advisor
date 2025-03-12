import os
import json
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from langchain.chains import LLMChain
from langchain_core.runnables import RunnableParallel
from datetime import datetime

load_dotenv()

# Initialize LLM
llm = ChatGroq(
    model="llama3-8b-8192",
    # api_key=api_key,
    temperature=0.1,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# Output parser that expects JSON object
json_parser = JsonOutputParser()


## Start of FIrst Implimentation

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
    input_variables=["user_input"],
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
    input_variables=["user_input"],
)

# Create parallel chains
csv_advice_chain = RunnableParallel(csv=csv_prompt | llm, advice=advice_prompt | llm)


# Main Pipeline First Implimentation
def financial_planner(user_input: str) -> tuple:
    result = csv_advice_chain.invoke({"user_input": user_input})
    return result["csv"].content, result["advice"].content


## End of FIrst Implimentation


## Start of Second Implimentation

# Prompts with strict JSON enforcement
income_prompt = PromptTemplate.from_template(
    "From this input: {input}, extract ONLY income sources and their monthly amounts. "
    "Do NOT include any expenses, total income, savings, debts, or costs. "
    "ONLY list actual sources of money (like Job, Freelancing, etc). "
    "Respond ONLY in this JSON format (no explanation, no text before/after): "
    '[{{"source": "Job", "amount": 4000}}, {{"source": "Freelancing", "amount": 500}}]'
)

expenses_prompt = PromptTemplate.from_template(
    "From this input: {input}, extract ONLY expenses and their monthly amounts. "
    "Do NOT include any income sources, total income, savings, or investments. "
    "Only include spending categories like Rent, Food, Subscriptions, etc. "
    "Respond ONLY in this JSON format (no explanation, no text before/after): "
    '[{{"category": "Rent", "amount": 1200}}, {{"category": "Food", "amount": 400}}]'
)

concerns_prompt = PromptTemplate.from_template(
    "Extract user's financial concerns and goals from this input: {input}. "
    "Respond only as plain text."
)

# Advice Generator
advice_prompt = PromptTemplate.from_template(
    "Based on this situation: {input}, "
    "provide clear, actionable financial advice. Keep it concise."
)

# Runnable chains
income_chain = income_prompt | llm
expenses_chain = expenses_prompt | llm
concerns_chain = concerns_prompt | llm

advice_chain = advice_prompt | llm

# Parallel Chain
budget_parallel_chain = RunnableParallel(
    income=income_chain,
    expenses=expenses_chain,
    concerns=concerns_chain,
    advice=advice_chain,
)


# Main Pipeline Second Implimentation
def run_budget_pipeline(user_input):
    extracted_data = budget_parallel_chain.invoke({"input": user_input})
    return extracted_data


## End of Second Implimentation
