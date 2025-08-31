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

# Mount static files for React build
if os.path.exists("frontend/build/static"):
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

# Mount favicon and other assets
if os.path.exists("frontend/build"):
    app.mount("/favicon.ico", StaticFiles(directory="frontend/build"), name="favicon")
    app.mount("/logo.png", StaticFiles(directory="frontend/build"), name="logo")
    app.mount("/logo-bear.png", StaticFiles(directory="frontend/build"), name="logo-bear")
    app.mount("/manifest.json", StaticFiles(directory="frontend/build"), name="manifest")

# Templates for server-side rendering
templates = Jinja2Templates(directory="frontend/build") if os.path.exists("frontend/build") else None


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        print(f"🔗 Connecting to database...")
        print(f"📊 Database URL: {settings.database_url[:50]}...")
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        # Don't fail startup completely, let health check handle it
        pass


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the React application"""
    if templates and os.path.exists("frontend/build/index.html"):
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        return HTMLResponse(
            content="<h1>ShortSelling.eu API</h1><p>Frontend not built. Visit /docs for API documentation.</p>",
            status_code=200
        )

# Catch-all route for React Router (SPA)
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_react_app(request: Request, full_path: str):
    """Serve React app for all non-API routes (SPA routing)"""
    # Don't intercept API routes
    if full_path.startswith("api/"):
        return HTMLResponse(content="Not Found", status_code=404)
    
    # Serve index.html for all other routes (React Router will handle routing)
    if templates and os.path.exists("frontend/build/index.html"):
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        return HTMLResponse(
            content="<h1>ShortSelling.eu API</h1><p>Frontend not built. Visit /docs for API documentation.</p>",
            status_code=200
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "app": settings.app_name, "version": settings.app_version}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
