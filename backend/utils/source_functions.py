import sqlite3
import traceback
from .constants import DB_PATH
import requests
from urllib.parse import urlparse

def db_connect():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    return conn,cursor


def check_url(url):
    # Clean up the URL first
    url = url.strip()
    
    # Handle URLs without protocol
    if not url.startswith(('http://', 'https://')):
        url = "https://" + url
    
    parsed = urlparse(url)
    
    # Basic URL format validation first
    if not parsed.netloc:
        print(f"Invalid URL format: {url}")
        return False
    
    print(f"Checking URL: {url}")
    print(f"Parsed netloc: {parsed.netloc}")
    
    # Try to validate with a request
    try:
        # Try HEAD request first (faster)
        print(f"Trying HEAD request for: {url}")
        response = requests.head(url, timeout=10, allow_redirects=True)
        print(f"HEAD response status: {response.status_code}")
        # Accept 2xx, 3xx, 403, and 401 (many sites block HEAD requests but are valid)
        if response.status_code < 400 or response.status_code in [401, 403]:
            return True
    except requests.RequestException as e:
        print(f"HEAD request failed: {e}")
    
    try:
        # If HEAD fails or returns 403, try GET request
        print(f"Trying GET request for: {url}")
        response = requests.get(url, timeout=10, allow_redirects=True)
        print(f"GET response status: {response.status_code}")
        # Accept 2xx, 3xx, 403, and 401 (many sites block automated requests but are valid)
        if response.status_code < 400 or response.status_code in [401, 403]:
            return True
    except requests.RequestException as e:
        print(f"GET request failed: {e}")
    
    return False

def add_source(client_id ,source_url):
    conn ,cur = db_connect()
    try :
        is_valid_url = check_url(source_url)
        print("is_valid is", is_valid_url)
        if is_valid_url :
            cur.execute("SELECT EXISTS (SELECT source_uel FROM source WHERE source_uel = '{}')".format(source_url))
            source_exists = cur.fetchone()[0]
        
            if not source_exists : 
                cur.execute("INSERT INTO source (source_uel) VALUES('{}')".format(source_url))
                conn.commit()
            
            cur.execute("SELECT source_id FROM source WHERE source_uel ='{}'".format(source_url))
            source_id = cur.fetchone()[0]
        
            cur.execute("SELECT EXISTS (SELECT client_id , source_id FROM client_source WHERE client_id ='{}' AND source_id = '{}')".format(client_id , source_id))
            row_exists = cur.fetchone()[0]

            if not row_exists : 
                cur.execute("INSERT INTO client_source (client_id , source_id) VALUES('{}' , '{}')".format(client_id , source_id))
                conn.commit()
                print("commited")
                return "added"  # Source was successfully added
            else : 
                return "exists"  # Source already exists for this client
        else :
            return "invalid"  # Invalid URL
    except Exception as e:
        print(traceback.print_exc())
        return "error"  # Error occurred

def add_client(client_id) :
    conn ,cur = db_connect()
    try : 
        cur.execute("SELECT EXISTS (SELECT client_id FROM client WHERE client_id ='{}')".format(client_id))
        client_exists = cur.fetchone()[0]
        if not client_exists : 
            cur.execute("INSERT INTO client (client_id) VALUES('{}')".format(client_id))
        conn.commit()
    except :
        print(traceback.print_exc())

def get_sources() :
    conn,cur = db_connect()
    cur.execute("SELECT source_uel FROM source")
    sources = cur.fetchall()
    source_list = [item[0] for item in sources]
    return source_list
