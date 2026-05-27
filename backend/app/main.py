from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, brigades, fields, requests, stats, users, wells

app = FastAPI(
    title="Нефтегаз API",
    description="API сайта нефтепромышленной компании: месторождения, скважины, заявки на обслуживание.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_prefix = "/api"
app.include_router(auth.router, prefix=api_prefix)
app.include_router(fields.router, prefix=api_prefix)
app.include_router(wells.router, prefix=api_prefix)
app.include_router(requests.router, prefix=api_prefix)
app.include_router(brigades.router, prefix=api_prefix)
app.include_router(users.router, prefix=api_prefix)
app.include_router(stats.router, prefix=api_prefix)


@app.get("/api/health")
def health():
    return {"status": "ok"}
