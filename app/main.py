from fastapi import FastAPI
import uvicorn

from app.api.employee_routes import router as employee_router
from app.api.insight_routes import router as insight_router
from app.database.init_db import init_db

app = FastAPI()

init_db()

app.include_router(employee_router)
app.include_router(insight_router)

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