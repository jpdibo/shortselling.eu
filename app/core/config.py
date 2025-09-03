import os
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Simple settings class - no Pydantic complications"""
    
    def __init__(self):
        # Application
        self.app_name = "ShortSelling.eu"
        self.app_version = "1.0.0"
        self.debug = False
        
        # Database - get from environment, fail if missing
        self.database_url = os.environ.get("DATABASE_URL")
        if not self.database_url:
            raise RuntimeError("DATABASE_URL environment variable is required!")
            
        print(f"🐛 LOADED DATABASE_URL: {self.database_url}")
        
        # Security
        self.secret_key = os.environ.get("SECRET_KEY", "your-secret-key-change-this-in-production")
        
        # Other settings
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.google_analytics_id = os.environ.get("GOOGLE_ANALYTICS_ID", "G-T14FW9YJ26")
        
        # Email
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_username = None
        self.smtp_password = None
        
        # Scraping
        self.scraping_interval_hours = 24
        self.max_retries = 3
        self.request_timeout = 30
        
        # Countries configuration
        self.countries = [
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


# Create settings instance
settings = Settings()