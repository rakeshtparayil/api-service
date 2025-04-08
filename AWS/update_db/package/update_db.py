import os
import psycopg
import datetime as dt
import json

def update_db(event, context):
    # Debug logging
    print("Event type:", type(event))
    print("Event content:", json.dumps(event, default=str))
    
    # Check what format the data is in and handle it appropriately
    if isinstance(event, dict):
        # If we receive a JSON payload with a 'body' field (common API Gateway pattern)
        if 'body' in event and event['body']:
            try:
                # If body is a JSON string, parse it
                if isinstance(event['body'], str):
                    body_data = json.loads(event['body'])
                else:
                    body_data = event['body']
                
                # Extract data from the parsed body
                data = [
                    body_data.get('timestamp'),
                    body_data.get('open'),
                    body_data.get('high'),
                    body_data.get('low'),
                    body_data.get('close')
                ]
            except Exception as e:
                print(f"Error parsing body: {e}")
                raise ValueError(f"Could not parse event body: {e}")
        else:
            # Direct dictionary access if no 'body' field
            data = [
                event.get('timestamp'),
                event.get('open'),
                event.get('high'),
                event.get('low'),
                event.get('close')
            ]
    else:
        # If event is already a list, use it directly
        data = event
    
    # Log the extracted data
    print("Extracted data:", data)
    
    # Check if timestamp exists
    if not data[0]:
        print("Missing timestamp in data:", data)
        raise ValueError("Timestamp is required but was not provided in the event")
    
    dbconn = os.getenv("DB_CONN")
    conn = psycopg.connect(dbconn)
    cur = conn.cursor()
    
    # Convert timestamp to datetime object
    data[0] = dt.datetime.fromtimestamp(float(data[0]))
    
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
    
    return {
        'statusCode': 200,
        'body': 'Data inserted successfully'
    }