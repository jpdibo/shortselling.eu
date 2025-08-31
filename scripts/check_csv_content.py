#!/usr/bin/env python3
"""
Check CSV Content
Check the actual content of the downloaded CSV to understand formatting issues
"""
import requests

def check_csv_content():
    """Check the CSV content directly"""
    print("🔍 Checking CSV Content")
    print("=" * 40)
    
    # Download the CSV directly
    csv_url = "https://www.bundesanzeiger.de/pub/en/nlp?0--top~csv~form~panel-form-csv~resource~link"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/csv,text/plain,*/*',
        'Accept-Language': 'en-US,en;q=0.9,de;q=0.8',
        'Referer': 'https://www.bundesanzeiger.de/pub/en/nlp?4',
    }
    
    try:
        response = requests.get(csv_url, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Content length: {len(response.content):,} bytes")
            
            # Show the first 1000 characters
            content = response.text
            print(f"\nFirst 1000 characters:")
            print("=" * 50)
            print(content[:1000])
            print("=" * 50)
            
            # Show the first 20 lines
            lines = content.split('\n')
            print(f"\nFirst 20 lines:")
            print("=" * 50)
            for i, line in enumerate(lines[:20]):
                print(f"{i+1:2d}: {repr(line)}")
            print("=" * 50)
            
            # Try different CSV parsing approaches
            print(f"\nTrying different CSV parsing approaches:")
            
            import pandas as pd
            from io import StringIO
            
            # Try with different separators
            separators = [',', ';', '\t']
            for sep in separators:
                try:
                    df = pd.read_csv(StringIO(content), sep=sep)
                    print(f"✅ Success with separator '{sep}': {len(df)} rows, {len(df.columns)} columns")
                    print(f"   Columns: {list(df.columns)}")
                    if len(df) > 0:
                        print(f"   First row: {df.iloc[0].tolist()}")
                    break
                except Exception as e:
                    print(f"❌ Failed with separator '{sep}': {e}")
            
            # Try with different encoding
            try:
                df = pd.read_csv(StringIO(content), encoding='utf-8-sig')
                print(f"✅ Success with utf-8-sig encoding: {len(df)} rows, {len(df.columns)} columns")
            except Exception as e:
                print(f"❌ Failed with utf-8-sig encoding: {e}")
            
            # Try with different line terminators
            try:
                df = pd.read_csv(StringIO(content), lineterminator='\r\n')
                print(f"✅ Success with \\r\\n line terminator: {len(df)} rows, {len(df.columns)} columns")
            except Exception as e:
                print(f"❌ Failed with \\r\\n line terminator: {e}")
            
        else:
            print(f"❌ Failed to download CSV")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_csv_content()
