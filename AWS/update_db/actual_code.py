import os
import psycopg
import datetime as dt
import argparse
import json

def update_db(data):
    # Get database connection string from environment or specify directly
    dbconn = os.getenv("DB_CONN")
    if not dbconn:
        print("Please set the DB_CONN environment variable with your PostgreSQL connection string")
        return
    
    conn = psycopg.connect(dbconn)
    cur = conn.cursor()
    
    # Convert timestamp to datetime object if it's a timestamp
    if isinstance(data[0], (int, float)):
        data[0] = dt.datetime.fromtimestamp(data[0])
    
    # Create table if it doesn't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS forex_data (
            date TIMESTAMP PRIMARY KEY,
            open FLOAT,
            high FLOAT,
            low FLOAT,
            close FLOAT
        );
    ''')

    # Insert data into the table
    cur.execute(
        '''
            INSERT INTO forex_data(date, open, high, low, close)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (date) DO NOTHING;
        ''', 
        tuple(data)
    )
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"Data successfully inserted for {data[0]}")
    print("Data is uploaded to database")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Update forex data in PostgreSQL database')
    parser.add_argument('--data', type=str, help='JSON array with format [timestamp/datetime, open, high, low, close]')
    parser.add_argument('--file', type=str, help='Path to JSON file with data')
    
    args = parser.parse_args()
    
    if args.data:
        data = json.loads(args.data)
        update_db(data)
    elif args.file:
        with open(args.file, 'r') as f:
            data = json.load(f)
        update_db(data)
    else:
        # Example demo data
        demo_data = [dt.datetime.now(), 1.1234, 1.1300, 1.1200, 1.1250]
        print("No data provided, using demo data:", demo_data)
        update_db(demo_data)