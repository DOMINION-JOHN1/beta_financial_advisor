from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import os

# from langchain_pipeline import run_budget_pipeline
from src.langchain_pipeline import financial_planner, run_budget_pipeline
from src.spreadsheet_generator import generate_budget_spreadsheet, parse_csv_content

app = FastAPI(title="AI Budget Generator", version="1.0")


class UserQuery(BaseModel):
    user_input: str


# Health check endpoint
@app.get("/")
def read_root():
    return {"message": "AI Budget Generator API is running."}


# Main budget generation endpoint
@app.post("/generate-budget")
async def generate_budget(request: UserQuery):
    try:
        # Process input through Langchain pipeline
        csv_output, advice = financial_planner(request.user_input)

        # Generate spreadsheet
        df_path = parse_csv_content(csv_output)

        app_domain = os.getenv("APP_DOMAIN")

        # Response
        return JSONResponse(
            {
                "message": "Budget generated successfully.",
                "download_link": (
                    f"{app_domain}/download/{df_path.split('/')[-1]}"
                    if df_path
                    else None
                ),
                "advice": advice,
            }
        )

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/generate-budget2")
async def generate_budget2(request: UserQuery):
    try:
        # Process input through Langchain pipeline
        result_data = run_budget_pipeline(request.user_input)

        # Generate spreadsheet
        file_path = generate_budget_spreadsheet(result_data)

        app_domain = os.getenv("APP_DOMAIN")

        # Response
        return JSONResponse(
            {
                "message": "Budget generated successfully.",
                "download_link": (
                    f"{app_domain}/download/{file_path.split('/')[-1]}"
                    if file_path
                    else None
                ),
                "advice": result_data["advice"].content,
            }
        )

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# Endpoint to download spreadsheet
@app.get("/download/{file_name}")
async def download_file(file_name: str):
    file_path = f"generated_sheets/{file_name}"
    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
