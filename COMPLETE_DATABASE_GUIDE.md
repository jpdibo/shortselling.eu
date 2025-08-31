Just use
conda activate short_selling (if cmd don't recognise use: )

para ativar database: "C:\Users\jpdib\anaconda3\envs\short_selling\Library\bin\pg_ctl.exe" ^
  -D "C:\Users\jpdib\anaconda3\envs\short_selling\Library\postgresql\data" ^
  -l "C:\Users\jpdib\anaconda3\envs\short_selling\Library\postgresql\pg.log" start

para ativar backend: python scripts/start.py
para ativar frontend:
   cd frontend
   npm start





# 🗄️ COMPLETE DATABASE GUIDE FOR SHORTSELLING.EU

## 🚨 **CRITICAL - READ THIS FIRST BEFORE ANY DATABASE OPERATIONS** 🚨

**THIS IS A PRODUCTION SYSTEM WITH REAL DATA - NEVER WIPE OR REINITIALIZE WITHOUT EXPLICIT PERMISSION**

---

## 🚀 **QUICK START - FASTEST WAY TO ACCESS DATABASE:**

```bash
# Start PostgreSQL (MUST DO THIS FIRST!)
"C:\Users\jpdib\anaconda3\envs\short_selling\Library\bin\pg_ctl.exe" -D "C:\Users\jpdib\anaconda3\envs\short_selling\Library\postgresql\data" start

# Check database status
"C:\Users\jpdib\anaconda3\envs\short_selling\Library\bin\psql.exe" -U jpdib -l

# Connect to main database
"C:\Users\jpdib\anaconda3\envs\short_selling\Library\bin\psql.exe" -U jpdib -d shortselling
```

---

## 🚫 **CRITICAL RULES - NEVER VIOLATE THESE:**

1. **NEVER run `initdb` or initialization scripts** on an existing database
2. **NEVER assume the database is empty** - ALWAYS check first
3. **NEVER delete or overwrite data** without explicit user permission
4. **ALWAYS use full paths** to PostgreSQL binaries (they're not in PATH)
5. **ALWAYS check existing data** before making any changes

---

## 📍 **CURRENT DATABASE STATE (as of 2025-08-26):**

### **Main Database (`shortselling`):**
- **Total Positions**: 311,826
- **Countries**: 12 (including Sweden)
- **Host**: localhost:5432
- **Username**: jpdib

### **Country Breakdown:**
```
GB (United Kingdom): 96,193 positions
DE (Germany):        52,143 positions  
FR (France):         35,228 positions
SE (Sweden):         32,671 positions ✅ INCLUDED
IT (Italy):          22,062 positions
NO (Norway):         20,764 positions
NL (Netherlands):    19,831 positions
ES (Spain):          12,864 positions
FI (Finland):         9,989 positions
DK (Denmark):         8,076 positions
BE (Belgium):         1,488 positions
IE (Ireland):           517 positions
```

### **Separate Databases:**
- `sweden_short_selling`: 32,671 positions (also in main DB)
- `norway_short_selling`: Norway-specific data

---

## 🔧 **DATABASE ACCESS COMMANDS (TESTED & WORKING):**

### **Start PostgreSQL:**
```bash
# Full path required - PostgreSQL is NOT in Windows PATH
"C:\Users\jpdib\anaconda3\envs\short_selling\Library\bin\pg_ctl.exe" -D "C:\Users\jpdib\anaconda3\envs\short_selling\Library\postgresql\data" start
```

### **List All Databases:**
```bash
"C:\Users\jpdib\anaconda3\envs\short_selling\Library\bin\psql.exe" -U jpdib -l
```

### **Connect to Main Database:**
```bash
"C:\Users\jpdib\anaconda3\envs\short_selling\Library\bin\psql.exe" -U jpdib -d shortselling
```

### **Quick Status Check:**
```bash
# Total positions
"C:\Users\jpdib\anaconda3\envs\short_selling\Library\bin\psql.exe" -U jpdib -d shortselling -c "SELECT COUNT(*) FROM short_positions;"

# Breakdown by country
"C:\Users\jpdib\anaconda3\envs\short_selling\Library\bin\psql.exe" -U jpdib -d shortselling -c "SELECT c.code, c.name, COUNT(sp.id) as positions FROM countries c JOIN short_positions sp ON c.id = sp.country_id GROUP BY c.code, c.name ORDER BY positions DESC;"
```

---

## 📤 **CSV EXPORT (TESTED & WORKING):**

### **Export Complete Database to CSV:**
```bash
# Export all positions to CSV with proper filename
"C:\Users\jpdib\anaconda3\envs\short_selling\Library\bin\psql.exe" -U jpdib -d shortselling -c "\copy (SELECT sp.date, co.name as company_name, co.isin, m.name as manager_name, c.code as country_code, c.name as country_name, sp.position_size, sp.is_active, sp.is_current FROM short_positions sp JOIN countries c ON sp.country_id = c.id JOIN companies co ON sp.company_id = co.id JOIN managers m ON sp.manager_id = m.id ORDER BY sp.date DESC) TO 'C:/shortselling.eu/backup/backup_complete_YYYYMMDD.csv' WITH CSV HEADER"
```

### **Export Specific Country:**
```bash
# Export only Sweden data
"C:\Users\jpdib\anaconda3\envs\short_selling\Library\bin\psql.exe" -U jpdib -d shortselling -c "\copy (SELECT sp.date, co.name, co.isin, m.name, c.code, c.name, sp.position_size FROM short_positions sp JOIN countries c ON sp.country_id = c.id JOIN companies co ON sp.company_id = co.id JOIN managers m ON sp.manager_id = m.id WHERE c.code = 'SE' ORDER BY sp.date DESC) TO 'C:/shortselling.eu/backup/sweden_only.csv' WITH CSV HEADER"
```

---

## 🔄 **DATA IMPORT/EXPORT OPERATIONS:**

### **Import Sweden Data into Main Database (if needed):**
```bash
# Enable dblink extension
"C:\Users\jpdib\anaconda3\envs\short_selling\Library\bin\psql.exe" -U jpdib -d shortselling -c "CREATE EXTENSION IF NOT EXISTS dblink;"

# Import Sweden positions from separate database
"C:\Users\jpdib\anaconda3\envs\short_selling\Library\bin\psql.exe" -U jpdib -d shortselling -c "INSERT INTO short_positions (date, company_id, manager_id, country_id, position_size, is_active, is_current, created_at) SELECT sp.date, sp.company_id, sp.manager_id, (SELECT id FROM countries WHERE code = 'SE') as country_id, sp.position_size, sp.is_active, sp.is_current, sp.created_at FROM dblink('host=localhost user=jpdib password=jpdib dbname=sweden_short_selling', 'SELECT date, company_id, manager_id, position_size, is_active, is_current, created_at FROM short_positions') AS sp(date date, company_id integer, manager_id integer, position_size numeric, is_active boolean, is_current boolean, created_at timestamp);"
```

---

## 🐍 **PYTHON ACCESS (WITH CONDA ENVIRONMENT):**

### **Test Database Connection:**
```bash
cmd /c "conda activate short_selling && python -c \"import sys; sys.path.append('C:\\shortselling.eu'); from app.db.database import get_db; db = next(get_db()); print('✅ Database connected'); db.close()\""
```

### **Get Database Statistics:**
```bash
cmd /c "conda activate short_selling && python -c \"import sys; sys.path.append('C:\\shortselling.eu'); from app.db.database import get_db; from app.db.models import ShortPosition; from sqlalchemy import func; db = next(get_db()); total = db.query(func.count(ShortPosition.id)).scalar(); print(f'Total positions: {total:,}'); db.close()\""
```

---

## 📊 **SCRAPERS AND DATA COLLECTION:**

### **Run Individual Country Scrapers:**
```bash
# Sweden scraper (adds to separate database)
cmd /c "conda activate short_selling && python C:\shortselling.eu\run_sweden_scraper.py"

# Norway scraper
cmd /c "conda activate short_selling && python C:\shortselling.eu\run_norway_scraper.py"
```

### **Daily Scraping (All Countries):**
```bash
cmd /c "conda activate short_selling && python C:\shortselling.eu\scripts\run_daily_scraping.py"
```

---

## 🗄️ **DATABASE ARCHITECTURE:**

### **Main Database (`shortselling`):**
- **Purpose**: Consolidated database with all countries
- **Contains**: 311,826+ positions from 12 countries
- **Tables**: `countries`, `companies`, `managers`, `short_positions`

### **Country-Specific Databases:**
- **`sweden_short_selling`**: Sweden data (also imported to main)
- **`norway_short_selling`**: Norway-specific processing

### **Backup Files Location:**
- **Path**: `C:\shortselling.eu\data_backup\`
- **CSV Exports**: `C:\shortselling.eu\backup\`

---

## ⚠️ **TROUBLESHOOTING:**

### **"Command not found" errors:**
- **Cause**: PostgreSQL binaries not in Windows PATH
- **Solution**: Always use full paths to executables

### **"Connection refused" errors:**
- **Cause**: PostgreSQL not started
- **Solution**: Run the pg_ctl start command first

### **Permission errors:**
- **Cause**: File/directory permissions or PostgreSQL not running as correct user
- **Solution**: Ensure PostgreSQL is running and check file permissions

### **Python import errors:**
- **Cause**: Wrong Python environment or missing project path
- **Solution**: Always use `conda activate short_selling` and add project to path

---

## 🔐 **SECURITY NOTES:**

- **Database User**: jpdib
- **Password**: (stored in .env file)
- **Access**: Local only (localhost)
- **Data**: Production data - handle with extreme care

---

## 📝 **COMMON OPERATIONS SUMMARY:**

1. **Start Database**: Use full path to `pg_ctl.exe`
2. **Check Status**: Use full path to `psql.exe` with `-l` flag
3. **Export CSV**: Use `\copy` command with full file paths
4. **Import Data**: Use `dblink` extension for cross-database operations
5. **Python Access**: Always activate conda environment first

---

## 🎯 **BEST PRACTICES:**

1. **Always check database state first** before making changes
2. **Use full paths** to all PostgreSQL executables
3. **Activate conda environment** before running Python scripts
4. **Export/backup data** before making significant changes
5. **Test commands** on small datasets first
6. **Never assume database is empty** - this is a production system

---

**Last Updated**: 2025-08-26  
**Database Status**: PRODUCTION - 311,826+ positions across 12 countries  
**Critical Note**: Sweden data successfully integrated into main database  

---

## 🚨 **EMERGENCY DATA RECOVERY:**

If database is accidentally wiped:
1. **Stop all operations immediately**
2. **Check backup files** in `C:\shortselling.eu\data_backup\`
3. **Run restoration script**: `python "C:\shortselling.eu\scripts\restore_backup_data.py"`
4. **Verify data integrity** after restoration

**Remember: This is a production system with months of real financial data. Handle with extreme care.**