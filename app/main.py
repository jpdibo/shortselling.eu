from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

from app.core.config import settings
from app.db.database import init_db
from app.api import countries, companies, managers, positions, analytics, subscriptions, csv_export, scraping, search

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Track and analyze short-selling positions across European countries. Get real-time insights into market activities and regulatory disclosures"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(countries.router, prefix="/api/countries", tags=["countries"])
app.include_router(companies.router, prefix="/api/companies", tags=["companies"])
app.include_router(managers.router, prefix="/api/managers", tags=["managers"])
app.include_router(positions.router, prefix="/api/positions", tags=["positions"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["subscriptions"])
app.include_router(csv_export.router, prefix="/api/csv", tags=["csv"])
app.include_router(scraping.router, prefix="/api", tags=["scraping"])
app.include_router(search.router, prefix="/api", tags=["search"])

# Mount static files (only if build directory and static subdirectory exist)
if os.path.exists("frontend/build/static"):
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

# Templates for server-side rendering
templates = Jinja2Templates(directory="frontend/build")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main application"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "app": settings.app_name, "version": settings.app_version}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
