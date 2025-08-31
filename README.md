# ShortSelling.eu

Track and analyze short-selling positions across Europe. Get real-time insights into the main market events.

## Project Overview

ShortSelling.eu is a comprehensive platform that tracks and analyzes short-selling positions disclosed by regulators across European countries. The platform provides real-time data, analytics, and insights into short-selling activities across 12 European jurisdictions with active data collection.

## Features

- **Real-time Data**: Daily scraping of short-selling disclosures from European regulators
- **Country-wise Analytics**: Track most shorted companies and top managers by country
- **Company Analysis**: Detailed breakdown of short positions by manager over time
- **Manager Profiles**: Individual pages for each manager with historical position data
- **Interactive Charts**: Time-series analysis with multiple timeframes (1M, 3M, 6M, 1Y, 2Y)
- **Global Analytics Dashboard**: Comprehensive overview of all European markets
- **Email Subscriptions**: Daily/weekly/monthly updates on new short positions
- **Fast Performance**: Pre-calculated database for optimal rendering speed
- **Responsive Design**: Modern UI with Tailwind CSS and mobile-friendly layout
- **Animated Typewriter Effect**: Engaging homepage with technological animations
- **Modern Typography**: Inter and JetBrains Mono fonts for professional appearance

## Supported Countries (Active Data)

### Currently Active (12 countries):
🇬🇧 United Kingdom, 🇩🇪 Germany, 🇫🇷 France, 🇸🇪 Sweden, 🇮🇹 Italy, 🇳🇴 Norway, 🇳🇱 Netherlands, 🇪🇸 Spain, 🇫🇮 Finland, 🇩🇰 Denmark, 🇧🇪 Belgium, 🇮🇪 Ireland

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: React with TypeScript
- **Styling**: Tailwind CSS with custom animations
- **Charts**: Plotly.js
- **Fonts**: Inter (headings), JetBrains Mono (monospace)
- **Deployment**: Docker-ready

## Setup Instructions

### Prerequisites

- Python 3.9+
- Anaconda environment: `short_selling`
- PostgreSQL database
- Node.js and npm

### Backend Installation

1. **Activate Anaconda Environment**:
   ```bash
   conda activate short_selling
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**:
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/shortselling
   SECRET_KEY=your-secret-key-here
   GOOGLE_ANALYTICS_ID=GA_MEASUREMENT_ID
   ```

4. **Database Setup**:
   ```bash
   python scripts/init_db.py
   ```

5. **Start the Backend**:
   ```bash
   python scripts/start.py
   ```

The backend will be available at `http://localhost:8000`

### Frontend Installation

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```

The frontend will be available at `http://localhost:3000`

## Project Structure

```
shortselling.eu/
├── app/
│   ├── api/                 # API endpoints
│   │   ├── analytics.py     # Analytics endpoints
│   │   ├── countries.py     # Country-specific endpoints
│   │   └── positions.py     # Position data endpoints
│   ├── core/               # Core configuration
│   ├── db/                 # Database models and migrations
│   ├── scrapers/           # Data scraping scripts
│   │   ├── base_scraper.py # Base scraper class
│   │   ├── france_scraper.py # France data scraper
│   │   ├── belgium_scraper.py # Belgium data scraper
│   │   └── ...             # Other country scrapers
│   ├── services/           # Business logic
│   │   └── daily_scraping_service.py # Data processing service
│   └── utils/              # Utility functions
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── AnimatedTagline.tsx    # Typewriter effect component
│   │   │   ├── CountrySelector.tsx    # Country selection interface
│   │   │   ├── Header.tsx             # Navigation header
│   │   │   ├── LatestPositions.tsx    # Recent positions display
│   │   │   └── ...                    # Other components
│   │   ├── pages/          # Page components
│   │   │   ├── HomePage.tsx           # Main homepage
│   │   │   ├── CountryPage.tsx        # Country-specific pages
│   │   │   └── ...                    # Other pages
│   │   ├── styles/         # Custom CSS
│   │   │   └── animations.css         # Custom animations
│   │   └── App.tsx         # Main app component
│   ├── public/             # Static assets
│   │   ├── logo.svg        # Main logo
│   │   ├── favicon.ico     # Favicon
│   │   └── manifest.json   # PWA manifest
│   ├── package.json        # Frontend dependencies
│   └── tailwind.config.js  # Tailwind CSS configuration
├── backup/                 # Database backups
├── scripts/                # Utility scripts
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Key Components

### Frontend Features

- **Animated Tagline**: Typewriter effect on homepage with modern typography
- **Country Selector**: Interactive country selection with real-time data updates
- **Subscription Form**: Email subscription for updates (header and homepage)
- **Responsive Design**: Mobile-friendly layout with Tailwind CSS
- **Modern UI**: Clean, professional design with technological aesthetics

### Backend Features

- **Multi-Country Scrapers**: Individual scrapers for each European country
- **Data Normalization**: Consistent data formatting across countries
- **Active Position Logic**: Smart detection of currently active short positions
- **API Endpoints**: RESTful API for frontend consumption
- **Database Optimization**: Efficient queries and indexing

## Database Backup

To create a backup of the database:

```bash
pg_dump -U jpdib -d shortselling > backup/backup_YYYY-MM-DD.sql
```

Or using the Anaconda environment:

```bash
"C:\Users\jpdib\anaconda3\envs\short_selling\Library\bin\pg_dump.exe" -U jpdib -d shortselling > backup/backup_2025-01-29.sql
```

## Recent Updates

- **Logo Update**: New vectorized SVG logo and favicon
- **Design Improvements**: Modern typography with Inter and JetBrains Mono fonts
- **Header Optimization**: Compact subscription form with better alignment
- **Tagline Enhancement**: Animated typewriter effect with updated messaging
- **Footer Updates**: Updated Buy Me a Coffee link and donation text

## Data Sources

The platform scrapes data from official regulatory websites across Europe. Each country has its own scraper module that handles the specific format and structure of their data. Currently active scrapers include France, Belgium, Germany, and other European countries.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is proprietary software. All rights reserved.

## Contact & Support

- **Email**: info@shortselling.eu
- **Donations**: [Buy Me a Coffee](https://buymeacoffee.com/econvibes)

This website is 100% free. Please consider donating to maintain the project running.
