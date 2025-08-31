from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    # Application
    app_name: str = "ShortSelling.eu"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database with UTF-8 encoding
    database_url: str = "postgresql://jpdib@localhost:5432/shortselling?client_encoding=utf8"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Google Analytics
    google_analytics_id: Optional[str] = None
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
