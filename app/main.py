from fastapi import FastAPI
import uvicorn

from app.api.employee_routes import router as employee_router

app = FastAPI()

app.include_router(employee_router)

@app.get("/")
def health_check():
    return {"message": "Salary Management Backend Running"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )