from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.auth_routes import router as auth_router
from app.api.employee_routes import router as employee_router
from app.api.insight_routes import router as insight_router
from app.core.config import settings
from app.database.init_db import init_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(auth_router)
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