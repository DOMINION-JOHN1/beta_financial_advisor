from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse

# from langchain_pipeline import run_budget_pipeline
from src.langchain_pipeline import run_budget_pipeline
from src.spreadsheet_generator import generate_budget_spreadsheet

app = FastAPI(title="AI Budget Generator", version="1.0")


# Health check endpoint
@app.get("/")
def read_root():
    return {"message": "AI Budget Generator API is running."}


# Main budget generation endpoint
@app.post("/generate-budget")
async def generate_budget(user_input: str = Form(...)):
    try:
        # Process input through Langchain pipeline
        result_data = run_budget_pipeline(user_input)

        # Generate spreadsheet
        file_path = generate_budget_spreadsheet(result_data)

        # Response
        return JSONResponse(
            {
                "message": "Budget generated successfully.",
                "download_link": f"/download/{file_path.split('/')[-1]}",
                "advice": result_data["advice"]["content"],
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
