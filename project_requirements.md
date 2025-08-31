# ShortSelling.eu Project Requirements

## Project Overview
Website to track short selling positions disclosed by regulators in Europe.
**Header**: "Daily updates on short-selling regulatory data from European countries"

## Database Structure
Columns will include:
- Date (the date that the short position was disclosed)
- Company (the company of which there is a short position)
- Manager (the positionholder or the manager who has the short position)
- Position size amount (as % → regulators require disclosure when above 0.5%)
- ISIN Code (in some cases available, in some not)

**Note**: Data order/sequence may vary by country - need to test each spreadsheet and save information/order for each country.

## Data Sources (Countries)

### High Priority Countries:
1. **Denmark**: https://oam.finanstilsynet.dk/#!/stats-and-extracts-individual-short-net-positions
2. **Norway**: https://ssr.finanstilsynet.no/
3. **Sweden**: https://www.fi.se/en/our-registers/net-short-positions
4. **Finland**: https://www.finanssivalvonta.fi/en/financial-market-participants/capital-markets/issuers-and-investors/short-positions
5. **Spain**: https://www.cnmv.es/DocPortal/Posiciones-Cortas/NetShortPositions.xls
6. **Germany**: https://www.bundesanzeiger.de/pub/en/nlp?4 (include historical positions)
7. **France**: https://www.data.gouv.fr/datasets/historique-des-positions-courtes-nettes-sur-actions-rendues-publiques-depuis-le-1er-novembre-2012/
8. **Italy**: https://www.consob.it/web/consob-and-its-activities/short-selling (two tabs: 'Correnti - Current' and 'Storiche - Historic')
9. **United Kingdom**: https://www.fca.org.uk/markets/short-selling/notification-disclosure-net-short-positions → https://www.fca.org.uk/publication/data/short-positions-daily-update.xlsx (two tabs: current and historic disclosures)
10. **Netherlands**: https://www.afm.nl/en/sector/registers/meldingenregisters/netto-shortposities-actueel and archive → https://www.afm.nl/en/sector/registers/meldingenregisters/netto-shortposities-historie
11. **Belgium**: https://www.fsma.be/en/shortselling and archive → https://www.fsma.be/en/shortselling-history
12. **Ireland**: https://www.centralbank.ie/regulation/industry-market-sectors/securities-markets/short-selling-regulation/public-net-short-positions
13. **Poland**: https://rss.knf.gov.pl/rss_pub/rssH.html (check historical positions and current positions)
14. **Austria**: https://webhost.fma.gv.at/ShortSelling/pub/www/QryNetShortPositions.aspx

### Low Priority Countries:
15. **Greece**: http://www.hcmc.gr/en_US/web/portal/shortselling1
16. **Portugal**: https://www.cmvm.pt/PInstitucional/Content?Input=39B47A118F62C7F232FC9D9D4B3BF11BE13616E84B12B2C3F3557C4784B84E07
17. **Luxembourg**: https://shortselling.apps.cssf.lu/

## Operational Requirements
- Website must be fast with very fast rendering time
- Pre-calculate data in database rather than calculating on frontend interaction
- Write scripts for each country to scrape data daily
- Update database and frontend with new scraped data
- Analytics graphs and charts must update with new information

## Functionality Requirements

### Country-Level Analytics:
For each country (as of most recent date):
1. **Most shorted companies** (cumulative % of active positions disclosed for each company)
2. **Manager with the most active short positions** in that country

### Company-Level Analytics:
For each company, show over time:
- Sum of active positions (% for each manager)
- Breakdown by manager (if two managers with 0.5% each = 1% total but shown as two separate 0.5% positions)
- Display in bar chart with different bars for different managers
- Legend below the chart
- Timeframes: (1) 1 month, (2) 3 months, (3) 6 months, (4) 1 year, (5) 2 years
- Daily data for (1), (2), (3); weekly data for (4), (5)

### Manager-Level Analytics:
For each manager:
1. **Number of active positions over time** (1% position in one company = 1 position; 10% in another company = second position)
   - Display in bar chart
   - Timeframes: (1) 1 month, (2) 3 months, (3) 6 months, (4) 1 year, (5) 2 years
   - Daily data for (1), (2), (3); weekly data for (4), (5)
2. **Current active and past historical positions** for each manager
3. **Individual manager pages** (e.g., shorteurope.eu/blackrock)
   - Chart over time of number of active positions for that manager (positions above 0.5%)

## Layout Requirements
- Flag emoji for each country next to its name
- White background with shades of grey when needed
- Black font color
- Colorful charts for easy manager differentiation

## Additional Requirements
- Google Analytics integration
- Terms of use page
- Privacy policy page
- Disclaimer (similar to shortsell.nl format)
- Subscription form at top of page:
  - "Get a daily email of all new short positions"
  - Toggle buttons: daily/weekly/monthly
  - Toggle buttons: all countries or specific country selection
  - Input fields: First Name and Email

## Technical Environment
- Use Anaconda environment: "C:\Users\jpdib\anaconda3\envs\short_selling"
- Fast, responsive web application
- Database-driven architecture for performance
- Automated data scraping and updates
