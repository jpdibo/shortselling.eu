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

# Serve individual assets from build directory
from fastapi.responses import FileResponse

@app.get("/favicon.ico")
async def get_favicon():
    return FileResponse("frontend/build/favicon.ico") if os.path.exists("frontend/build/favicon.ico") else FileResponse("frontend/build/logo.jpeg")

@app.get("/logo.png")
async def get_logo():
    return FileResponse("frontend/build/logo.png") if os.path.exists("frontend/build/logo.png") else None

@app.get("/logo-bear.png") 
async def get_logo_bear():
    return FileResponse("frontend/build/logo-bear.png") if os.path.exists("frontend/build/logo-bear.png") else None

@app.get("/manifest.json")
async def get_manifest():
    return FileResponse("frontend/build/manifest.json") if os.path.exists("frontend/build/manifest.json") else None

# Templates for server-side rendering
templates = Jinja2Templates(directory="frontend/build") if os.path.exists("frontend/build") else None


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        print(f"🔗 Connecting to database...")
        print(f"📊 DATABASE_URL from env: {os.environ.get('DATABASE_URL', 'NOT SET')[:30]}...")
        print(f"📊 Settings database_url: {settings.database_url[:30]}...")
        print(f"🌍 Environment: {'PRODUCTION' if 'localhost' not in settings.database_url else 'DEVELOPMENT'}")
        print(f"🔄 Config loaded at startup")
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print(f"❌ Exception type: {type(e).__name__}")
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

# Add middleware to log requests for debugging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"🔍 Request: {request.method} {request.url}")
    response = await call_next(request)
    print(f"✅ Response: {response.status_code}")
    return response

# Catch-all route for React Router (SPA)
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_react_app(request: Request, full_path: str):
    """Serve React app for all non-API routes (SPA routing)"""
    # Don't intercept API routes - let them return 404 naturally
    if full_path.startswith("api/"):
        return HTMLResponse(content=f"API endpoint not found: /{full_path}", status_code=404)
    
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

@app.get("/debug")
async def debug_info():
    """Debug information for deployment troubleshooting"""
    return {
        "frontend_build_exists": os.path.exists("frontend/build"),
        "index_html_exists": os.path.exists("frontend/build/index.html"),
        "logo_bear_exists": os.path.exists("frontend/build/logo-bear.png"),
        "static_dir_exists": os.path.exists("frontend/build/static"),
        "database_url": settings.database_url[:50] + "...",
        "working_directory": os.getcwd(),
        "environment": "production" if os.environ.get('RAILWAY_ENVIRONMENT') else "development"
    }

@app.post("/initialize-db")
async def initialize_database():
    """Initialize the database with tables and countries"""
    try:
        # Run the same initialization as the script
        from app.db.models import Country
        from app.db.database import SessionLocal
        
        db = SessionLocal()
        
        # Check if countries already exist
        existing_countries = db.query(Country).count()
        if existing_countries > 0:
            return {"status": "success", "message": f"Database already initialized with {existing_countries} countries"}
        
        # Add countries from settings
        for country_data in settings.countries:
            country = Country(
                code=country_data['code'],
                name=country_data['name'],
                flag=country_data['flag'],
                priority=country_data['priority'],
                url=country_data['url'],
                is_active=True
            )
            db.add(country)
        
        db.commit()
        db.close()
        
        return {"status": "success", "message": f"Successfully initialized database with {len(settings.countries)} countries"}
        
    except Exception as e:
        return {"status": "error", "message": f"Failed to initialize database: {str(e)}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
