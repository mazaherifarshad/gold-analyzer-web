from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.status import router as status_router
from api.analysis import router as analysis_router
from api.market import router as market_router

from scheduler import start_scheduler


app = FastAPI(
    title="Gold Analyzer Pro",
    version="2.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(status_router)
app.include_router(market_router)
app.include_router(analysis_router)


@app.on_event("startup")
def startup():

    start_scheduler()