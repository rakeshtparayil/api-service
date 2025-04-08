import os
import psycopg
import datetime as dt

def update_db(event, context):
    data = event
    dbconn = os.getenv("DB_CONN")
    conn = psycopg.connect(dbconn)
    cur = conn.cursor()
    
    # Convert timestamp to datetime object
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