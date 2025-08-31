import os
from typing import Optional, List
from pydantic import BaseModel, Field, SecretStr, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


def _maybe_build_from_pg_parts() -> Optional[str]:
    """Build a postgres URL if DATABASE_URL/POSTGRES_URL are absent but PG* parts exist."""
    host = os.getenv("PGHOST")
    db = os.getenv("PGDATABASE") 
    user = os.getenv("PGUSER")
    pwd = os.getenv("PGPASSWORD")
    port = os.getenv("PGPORT", "5432")
    
    if all([host, db, user, pwd]):
        return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}?sslmode=require"
    return None


class Settings(BaseSettings):
    # Application
    app_name: str = "ShortSelling.eu"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database - accept DATABASE_URL or POSTGRES_URL
    database_url: SecretStr = Field(
        ...,
        validation_alias=AliasChoices('DATABASE_URL', 'POSTGRES_URL')
    )
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Security
    secret_key: SecretStr = Field(
        default="your-secret-key-change-this-in-production"
    )
    
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Google Analytics
    google_analytics_id: Optional[str] = "G-T14FW9YJ26"
    
    # Email
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # Scraping
    scraping_interval_hours: int = 24
    max_retries: int = 3
    request_timeout: int = 30
    
    # Countries configuration
    countries: List[dict] = [
        {"code": "DK", "name": "Denmark", "flag": "DK", "priority": "high", "url": "https://oam.finanstilsynet.dk/#!/stats-and-extracts-individual-short-net-positions"},
        {"code": "NO", "name": "Norway", "flag": "NO", "priority": "high", "url": "https://ssr.finanstilsynet.no/"},
        {"code": "SE", "name": "Sweden", "flag": "SE", "priority": "high", "url": "https://www.fi.se/en/our-registers/net-short-positions"},
        {"code": "FI", "name": "Finland", "flag": "FI", "priority": "high", "url": "https://www.finanssivalvonta.fi/en/financial-market-participants/capital-markets/issuers-and-investors/short-positions"},
        {"code": "ES", "name": "Spain", "flag": "ES", "priority": "high", "url": "https://www.cnmv.es/DocPortal/Posiciones-Cortas/NetShortPositions.xls"},
        {"code": "DE", "name": "Germany", "flag": "DE", "priority": "high", "url": "https://www.bundesanzeiger.de/pub/en/nlp?4"},
        {"code": "FR", "name": "France", "flag": "FR", "priority": "high", "url": "https://www.data.gouv.fr/datasets/historique-des-positions-courtes-nettes-sur-actions-rendues-publiques-depuis-le-1er-novembre-2012/"},
        {"code": "IT", "name": "Italy", "flag": "IT", "priority": "high", "url": "https://www.consob.it/web/consob-and-its-activities/short-selling"},
        {"code": "GB", "name": "United Kingdom", "flag": "GB", "priority": "high", "url": "https://www.fca.org.uk/markets/short-selling/notification-disclosure-net-short-positions"},
        {"code": "NL", "name": "Netherlands", "flag": "NL", "priority": "high", "url": "https://www.afm.nl/en/sector/registers/meldingenregisters/netto-shortposities-actueel"},
        {"code": "BE", "name": "Belgium", "flag": "BE", "priority": "high", "url": "https://www.fsma.be/en/shortselling"},
        {"code": "IE", "name": "Ireland", "flag": "IE", "priority": "high", "url": "https://www.centralbank.ie/regulation/industry-market-sectors/securities-markets/short-selling-regulation/public-net-short-positions"},
        {"code": "PL", "name": "Poland", "flag": "PL", "priority": "high", "url": "https://rss.knf.gov.pl/rss_pub/rssH.html"},
        {"code": "AT", "name": "Austria", "flag": "AT", "priority": "high", "url": "https://webhost.fma.gv.at/ShortSelling/pub/www/QryNetShortPositions.aspx"},
        {"code": "GR", "name": "Greece", "flag": "GR", "priority": "low", "url": "http://www.hcmc.gr/en_US/web/portal/shortselling1"},
        {"code": "PT", "name": "Portugal", "flag": "PT", "priority": "low", "url": "https://www.cmvm.pt/PInstitucional/Content?Input=39B47A118F62C7F232FC9D9D4B3BF11BE13616E84B12B2C3F3557C4784B84E07"},
        {"code": "LU", "name": "Luxembourg", "flag": "LU", "priority": "low", "url": "https://shortselling.apps.cssf.lu/"}
    ]
    
    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Try to build from PG parts if main URL vars are missing
_built = _maybe_build_from_pg_parts()
if _built and not (os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")):
    os.environ["DATABASE_URL"] = _built

# Use Railway's automatic DATABASE_URL environment variable
# No hardcoded fallback - let Railway manage the connection

# Instantiate settings with clear error messages
try:
    settings = Settings()
    print(f"✅ Settings loaded successfully")
    print(f"📊 Database URL set: {settings.database_url.get_secret_value()[:50]}...")
except Exception as e:
    missing_url = not (os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or _maybe_build_from_pg_parts())
    if missing_url:
        raise RuntimeError(
            "Missing database URL. Set one of:\n"
            "  - DATABASE_URL (preferred)\n"
            "  - POSTGRES_URL\n" 
            "  - or PGHOST/PGDATABASE/PGUSER/PGPASSWORD (+ optional PGPORT)\n"
            "Example: DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname?sslmode=require"
        ) from e
    raise
