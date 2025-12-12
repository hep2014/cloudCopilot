from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import llm_router
from app.routers.api_test_router import router as api_test_router

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:80", "http://frontend"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(llm_router.router)
app.include_router(api_test_router)
